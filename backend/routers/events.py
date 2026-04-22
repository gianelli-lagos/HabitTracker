from datetime import date, datetime
from typing import List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models.user import User
from routers.auth import get_current_user
from services.event_service import (
    create_event,
    get_user_events,
    get_event_by_id,
    update_event,
    delete_event,
    invite_users,
    update_event_invites,
    respond_to_invite,
    get_event_attendees,
)
from services.notification_service import create_notification


router = APIRouter(prefix="/events", tags=["events"])


# Request schemas
class EventCreate(BaseModel):
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    invite_user_ids: List[int] = []


class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    location: Optional[str] = None


class InviteUsersBody(BaseModel):
    user_ids: List[int]


class RespondBody(BaseModel):
    status: str  # 'accepted' or 'declined'


# Response schemas
class UserInfo(BaseModel):
    id: int
    username: str
    
    class Config:
        from_attributes = True


class EventAttendeeResponse(BaseModel):
    id: Optional[int]
    event_id: Optional[int]
    user_id: int
    status: str
    invited_at: Optional[datetime]
    responded_at: Optional[datetime]
    user: Optional[UserInfo]
    
    class Config:
        from_attributes = True


class EventResponse(BaseModel):
    id: int
    creator_id: int
    title: str
    description: Optional[str]
    start_time: datetime
    end_time: datetime
    location: Optional[str]
    created_at: Optional[datetime]
    attendees: List[EventAttendeeResponse] = []
    
    class Config:
        from_attributes = True


@router.post("", response_model=EventResponse)
def create_event_endpoint(
    body: EventCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create an event and optionally invite users in one shot.
    Returns the created Event row.
    """
    event = create_event(
        db=db,
        creator_id=current_user.id,
        title=body.title,
        description=body.description,
        start_time=body.start_time,
        end_time=body.end_time,
        location=body.location,
    )

    if body.invite_user_ids:
        new_attendees = invite_users(db, event.id, current_user.id, body.invite_user_ids)

        # Send notifications to newly invited users
        for attendee in new_attendees:
            create_notification(
                db=db,
                user_id=attendee.user_id,
                type="event_invite",
                title=f"📅 Event Invitation: {event.title}",
                message=f"{current_user.username} invited you to {event.title}",
                data={
                    "event_id": event.id,
                    "start_time": event.start_time.isoformat() if event.start_time else None,
                    "location": event.location,
                },
            )

    return event


@router.get("", response_model=List[EventResponse])
def get_events_endpoint(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get events the current user created or is invited to.
    Optional date range lets the calendar page load a specific window.
    """
    return get_user_events(db, current_user.id, start_date, end_date)


@router.get("/{event_id}", response_model=EventResponse)
def get_event_endpoint(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get one event (creator or invited users only)."""
    return get_event_by_id(db, event_id, current_user.id)


@router.put("/{event_id}", response_model=EventResponse)
def update_event_endpoint(
    event_id: int,
    body: EventUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update core fields of an event. Only the creator can do this."""
    return update_event(db, event_id, current_user.id, **body.model_dump())


@router.delete("/{event_id}")
def delete_event_endpoint(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete an event. Only the creator can do this."""
    return delete_event(db, event_id, current_user.id)


@router.post("/{event_id}/invite")
def invite_users_endpoint(
    event_id: int,
    body: InviteUsersBody,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Invite additional users to an existing event.
    Also sends notification rows for each newly invited user.
    """
    event = get_event_by_id(db, event_id, current_user.id)

    new_attendees = invite_users(db, event_id, current_user.id, body.user_ids)
    for attendee in new_attendees:
        create_notification(
            db=db,
            user_id=attendee.user_id,
            type="event_invite",
            title=f"📅 Event Invitation: {event.title}",
            message=f"{current_user.username} invited you to {event.title}",
            data={
                "event_id": event.id,
                "start_time": event.start_time.isoformat() if event.start_time else None,
                "location": event.location,
            },
        )

    return {"invited_user_ids": [a.user_id for a in new_attendees]}


@router.put("/{event_id}/invites")
def update_invites_endpoint(
    event_id: int,
    body: InviteUsersBody,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update the invites for an event.
    Syncs attendees: adds new users, removes users not in the list, keeps existing ones.
    Only the creator can do this.
    """
    event = get_event_by_id(db, event_id, current_user.id)
    result = update_event_invites(db, event_id, current_user.id, body.user_ids)
    
    # Send notifications for newly invited users
    for attendee in result.get("new_attendees", []):
        create_notification(
            db=db,
            user_id=attendee.user_id,
            type="event_invite",
            title=f"📅 Event Invitation: {event.title}",
            message=f"{current_user.username} invited you to {event.title}",
            data={
                "event_id": event.id,
                "start_time": event.start_time.isoformat() if event.start_time else None,
                "location": event.location,
            },
        )
    
    return result


@router.put("/{event_id}/respond", response_model=EventAttendeeResponse)
def respond_endpoint(
    event_id: int,
    body: RespondBody,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Accept or decline an invitation for the current user.
    """
    return respond_to_invite(db, event_id, current_user.id, body.status)


@router.get("/{event_id}/attendees", response_model=List[EventAttendeeResponse])
def attendees_endpoint(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List all attendees for an event (with their status).
    Creator or invited users only.
    """
    return get_event_attendees(db, event_id, current_user.id)

