from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone, date
from database import get_db
from routers.auth import get_current_user
from models.user import User
from models.habit import HabitLog
from services.habit_service import (
    createHabit,
    getUserHabits,
    getHabitByID,
    updateHabit,
    deleteHabit,
    logHabit,
    getHabitLogs, 
    getUserStats
)
from services.notification_service import create_notification

router = APIRouter(prefix="/habits", tags=["habits"])


#GET    /habits/logs/all   Get all habit logs for heatmap (must be before /{habit_id} routes)
@router.get("/logs/all")
def get_all_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    results = (
        db.query(
            func.date(HabitLog.date).label("date"),
            func.count(HabitLog.id).label("count")
        )
        .filter(HabitLog.user_id == current_user.id)
        .group_by(func.date(HabitLog.date))
        .all()
    )
    return [
        {
            "date": r.date.isoformat() if r.date else None,
            "count": int(r.count)
        }
        for r in results
    ]


#POST   /habits   Create new habit
@router.post("")
def create_habit(
    name: str,
    description: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return createHabit(db, current_user.id, name, description)


#GET    /habits  Get all user's habits
@router.get("")
def get_habits(
    active_only: bool = True,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return getUserHabits(db, current_user.id, active_only)

@router.get("/stats")
def read_user_stats(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return getUserStats(db, user_id=current_user.id)


#GET    /habits/{id}   Get single habit
@router.get("/{habit_id}")
def get_habit(
    habit_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return getHabitByID(db, habit_id, current_user.id)


#PUT    /habits/{id}  Update habit
@router.put("/{habit_id}")
def update_habit(
    habit_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return updateHabit(db, habit_id, current_user.id, name, description)


#DELETE /habits/{id}  Delete (soft delete)
@router.delete("/{habit_id}")
def delete_habit(
    habit_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return deleteHabit(db, habit_id, current_user.id)


#POST   /habits/{id}/log   Log habit for today
@router.post("/{habit_id}/log")
def log_habit(
    habit_id: int,
    log_date: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if log_date is None:
        log_date = datetime.now(timezone.utc).astimezone().date()

    log = logHabit(db, habit_id, current_user.id, log_date)
    habit = getHabitByID(db, habit_id, current_user.id)

    if habit.current_streak in [7, 30, 100, 365]:
        create_notification(
            db=db,
            user_id=current_user.id,
            type='milestone',
            title=f'🎉 {habit.current_streak} Day Streak!',
            message=f'Incredible! You have maintained "{habit.name}" for {habit.current_streak} days!'
        )
    return log


#GET    /habits/{id}/logs  Get habit completion history
@router.get("/{habit_id}/logs")
def get_logs(
    habit_id: int,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return getHabitLogs(
        db,
        habit_id,
        current_user.id,
        start_date,
        end_date
    )


#GET    /habits/{id}/stats   Get streak stats
@router.get("/{habit_id}/stats")
def get_habit_stats(
    habit_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # verify habit exists + belongs to user
    habit = getHabitByID(db, habit_id, current_user.id)

    logs = (
        db.query(HabitLog)
        .filter(
            and_(
                HabitLog.habit_id == habit_id,
                HabitLog.user_id == current_user.id
            )
        )
        .order_by(HabitLog.date.desc())
        .all()
    )

    total_logs = len(logs)
    last_logged_date = logs[0].date if logs else None

    return {
        "current_streak": habit.current_streak,
        "longest_streak": habit.longest_streak,
        "total_logs": total_logs,
        "last_logged_date": last_logged_date
    }



