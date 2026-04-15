from __future__ import annotations

from datetime import date, datetime, time
from typing import Iterable, Optional

from fastapi import HTTPException, status
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from models.event import Event, EventAttendee
from models.user import User


def _range_to_datetimes(start_date: Optional[date], end_date: Optional[date]):
    """Convert optional date boundaries into full-day datetime boundaries."""
    start_dt = datetime.combine(start_date, time.min) if start_date else None
    end_dt = datetime.combine(end_date, time.max) if end_date else None
    return start_dt, end_dt


def create_event(
    db: Session,
    creator_id: int,
    title: str,
    description: Optional[str],
    start_time: datetime,
    end_time: datetime,
    location: Optional[str],
):
    """Create a calendar event owned by creator_id."""
    if end_time <= start_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="end_time must be after start_time",
        )

    event = Event(
        creator_id=creator_id,
        title=title,
        description=description,
        start_time=start_time,
        end_time=end_time,
        location=location,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def get_user_events(
    db: Session,
    user_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
):
    """
    Get events that the user either:
    - created, or
    - is invited to (any status).
    Optionally restricted to a date range, based on event-time overlap.
    """
    start_dt, end_dt = _range_to_datetimes(start_date, end_date)

    query = (
        db.query(Event)
        .outerjoin(EventAttendee, EventAttendee.event_id == Event.id)
        .filter(or_(Event.creator_id == user_id, EventAttendee.user_id == user_id))
        .distinct()
    )

    # Overlap filter: event’s time window intersects [start_dt, end_dt]
    if start_dt is not None:
        query = query.filter(Event.end_time >= start_dt)
    if end_dt is not None:
        query = query.filter(Event.start_time <= end_dt)

    return query.order_by(Event.start_time.asc()).all()


def get_event_by_id(db: Session, event_id: int, user_id: int):
    """Return event if user is creator or attendee; otherwise 403."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

    is_creator = event.creator_id == user_id
    is_attendee = (
        db.query(EventAttendee)
        .filter(and_(EventAttendee.event_id == event_id, EventAttendee.user_id == user_id))
        .first()
        is not None
    )
    if not (is_creator or is_attendee):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this event",
        )

    return event


def update_event(db: Session, event_id: int, creator_id: int, **updates):
    """Allow only the creator to edit core fields of an event."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    if event.creator_id != creator_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the creator can update this event",
        )

    allowed_fields = {"title", "description", "start_time", "end_time", "location"}
    # Strip out disallowed or None-valued fields
    for k, v in list(updates.items()):
        if k not in allowed_fields or v is None:
            updates.pop(k, None)

    if "start_time" in updates or "end_time" in updates:
        new_start = updates.get("start_time", event.start_time)
        new_end = updates.get("end_time", event.end_time)
        if new_end <= new_start:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="end_time must be after start_time",
            )

    for field, value in updates.items():
        setattr(event, field, value)

    db.commit()
    db.refresh(event)
    return event


def delete_event(db: Session, event_id: int, creator_id: int):
    """Hard-delete an event; only the creator can do this."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    if event.creator_id != creator_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the creator can delete this event",
        )

    db.delete(event)
    db.commit()
    return {"detail": "Event deleted"}


def invite_users(db: Session, event_id: int, creator_id: int, user_ids: Iterable[int]):
    """
    Add attendees for this event (creator-only).
    - Skips the creator.
    - Skips users already invited.
    - Validates that all target users exist.
    Returns the new EventAttendee rows.
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    if event.creator_id != creator_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the creator can invite users",
        )

    normalized_ids = {int(uid) for uid in user_ids if int(uid) != creator_id}
    if not normalized_ids:
        return []

    existing = (
        db.query(EventAttendee)
        .filter(and_(EventAttendee.event_id == event_id, EventAttendee.user_id.in_(normalized_ids)))
        .all()
    )
    existing_ids = {a.user_id for a in existing}

    # Validate that the users exist
    users = db.query(User).filter(User.id.in_(normalized_ids)).all()
    found_ids = {u.id for u in users}
    missing = sorted(list(normalized_ids - found_ids))
    if missing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Users not found: {missing}",
        )

    new_rows = []
    for uid in normalized_ids:
        if uid in existing_ids:
            continue
        attendee = EventAttendee(event_id=event_id, user_id=uid, status="invited")
        db.add(attendee)
        new_rows.append(attendee)

    db.commit()
    for row in new_rows:
        db.refresh(row)
    return new_rows


def respond_to_invite(db: Session, event_id: int, user_id: int, status_value: str):
    """
    Update the current user's invitation status for the given event.
    Only 'accepted' or 'declined' are allowed.
    """
    if status_value not in {"accepted", "declined"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="status must be 'accepted' or 'declined'",
        )

    attendee = (
        db.query(EventAttendee)
        .filter(and_(EventAttendee.event_id == event_id, EventAttendee.user_id == user_id))
        .first()
    )
    if not attendee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invitation not found")

    attendee.status = status_value
    attendee.responded_at = datetime.utcnow()
    db.commit()
    db.refresh(attendee)
    return attendee


def get_event_attendees(db: Session, event_id: int, user_id: int):
    """
    List attendees for an event.
    Caller must be the creator or an invited user (enforced via get_event_by_id).
    """
    # Authorization & existence check
    get_event_by_id(db, event_id, user_id)

    return (
        db.query(EventAttendee)
        .filter(EventAttendee.event_id == event_id)
        .order_by(EventAttendee.invited_at.asc())
        .all()
    )
