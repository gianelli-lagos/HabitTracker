from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from fastapi import HTTPException, status
from datetime import date

from models.habit import Habit, HabitLog


def createHabit(
        db: Session, 
        user_id: int, 
        name: str, 
        description: str
    ):
    habit = Habit(
        user_id=user_id,
        name=name,
        description=description,
    )
    db.add(habit)
    db.commit()
    db.refresh(habit)
    return habit


def getUserHabits(
        db: Session, 
        user_id: int, 
        active_only: bool = True
    ):
    query = db.query(Habit).filter(Habit.user_id == user_id)
    if active_only:
        query = query.filter(Habit.is_active == True)
    return query.order_by(Habit.created_at.desc()).all()


def getHabitByID(
        db: Session, 
        habit_id: int, 
        user_id: int
    ):
    habit = db.query(Habit).filter(and_(Habit.id == habit_id, Habit.user_id == user_id)).first()
    if not habit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Habit not found")
    return habit


def updateHabit(
        db: Session, 
        habit_id: int, 
        user_id: int, 
        name: str = None, 
        description: str = None
    ):
    habit = getHabitByID(db, habit_id, user_id)
    if name is not None:
        habit.name = name
    if description is not None:
        habit.description = description
    db.commit()
    db.refresh(habit)
    return habit


def deleteHabit(
        db: Session, 
        habit_id: int, 
        user_id: int
    ):
    habit = getHabitByID(db, habit_id, user_id)
    habit.is_active = False
    db.commit()
    return {"detail": "Habit deleted"}


def logHabit(
        db: Session, 
        habit_id: int, 
        user_id: int, 
        log_date: date = None
    ):
    if log_date is None:
        log_date = date.today()

    habit = getHabitByID(db, habit_id, user_id)

    # check for duplicate logs for the same day
    existing = db.query(HabitLog).filter(
        and_(
            HabitLog.habit_id == habit_id,
            HabitLog.user_id == user_id,
            HabitLog.date == log_date,
        )).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Habit already logged for this date")

    log = HabitLog(habit_id=habit_id, user_id=user_id, date=log_date)
    db.add(log)

    # recalculate current streak
    all_logs = (
        db.query(HabitLog)
        .filter(and_(HabitLog.habit_id == habit_id, HabitLog.user_id == user_id))
        .order_by(HabitLog.date.desc())
        .all()
    )
    logged_dates = sorted({l.date for l in all_logs} | {log_date}, reverse=True)

    streak = 1
    for i in range(1, len(logged_dates)):
        delta = (logged_dates[i - 1] - logged_dates[i]).days
        if delta == 1:
            streak += 1
        else:
            break

    habit.current_streak = streak
    if streak > habit.longest_streak:
        habit.longest_streak = streak

    db.commit()
    db.refresh(log)
    return log


def getHabitLogs(
        db: Session, 
        habit_id: int, 
        user_id: int, 
        start_date: date = None, 
        end_date: date = None
    ):
    # verify ownership
    getHabitByID(db, habit_id, user_id)

    query = db.query(HabitLog).filter(and_(HabitLog.habit_id == habit_id, HabitLog.user_id == user_id))
    if start_date:
        query = query.filter(HabitLog.date >= start_date)
    if end_date:
        query = query.filter(HabitLog.date <= end_date)

    return query.order_by(HabitLog.date.desc()).all()

def getUserStats(db: Session, user_id: int):
    # toal active habits
    habits = db.query(Habit).filter(Habit.user_id == user_id, Habit.is_active == True).all()
    total_habits = len(habits)
    if total_habits == 0:
        return {
            "total_habits": 0,
            "success_rate": 0,
            "longest_streak": 0
        }
    # longest streak 
    longest_streak = max([h.longest_streak for h in habits])

    # success rate
    # Total Logs / Total Days since each habit was created
    total_logs = db.query(HabitLog).filter(HabitLog.user_id == user_id).count()
    
    total_possible_days = 0
    for habit in habits:
        # Calculate days from creation until today
        delta = (date.today() - habit.created_at.date()).days + 1
        total_possible_days += max(1, delta) # minimum one day

    success_rate = (total_logs / total_possible_days) * 100

    return {
        "total_habits": total_habits,
        "success_rate": round(min(success_rate, 100), 1), # Cap at 100%
        "longest_streak": longest_streak
    }