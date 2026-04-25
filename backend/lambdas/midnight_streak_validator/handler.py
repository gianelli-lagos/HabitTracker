import sys
import os
from datetime import date

# Add paths for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(parent_dir)

sys.path.append(parent_dir)
sys.path.append(project_root)

from shared.db_connection import get_db_session
from shared.logger import log_info, log_error
from models.habit import Habit, HabitLog
from services.notification_service import create_notification

def lambda_handler(event, context):
    """
    Runs at midnight (12:00 AM EDT)
    
    Checks all habits with active streaks
    If habit was NOT logged today, resets streak to 0
    Creates "streak broken" notification
    """
    log_info("Starting midnight streak validation")
    
    try:
        db = get_db_session()
        today = date.today()
        reset_count = 0
        
        # Get all habits with active streaks
        habits = db.query(Habit).filter(Habit.current_streak > 0).all()
        
        log_info(f"Checking {len(habits)} habits with active streaks")
        
        for habit in habits:
            # Check if habit was logged today
            logged_today = db.query(HabitLog).filter(
                HabitLog.habit_id == habit.id,
                HabitLog.date == today
            ).first()
            
            if not logged_today:
                # User didn't log today - reset streak
                old_streak = habit.current_streak
                habit.current_streak = 0
                db.commit()
                
                reset_count += 1
                
                log_info(
                    "Streak reset",
                    habit_id=habit.id,
                    user_id=habit.user_id,
                    old_streak=old_streak
                )
                
                # Create notification
                create_notification(
                    db=db,
                    user_id=habit.user_id,
                    type='streak_broken',
                    title='Streak Reset 😔',
                    message=f'Your {habit.name} streak was reset because you didn\'t log today.',
                    data={
                        'habit_id': habit.id,
                        'habit_name': habit.name,
                        'lost_streak': old_streak
                    }
                )
        
        db.close()
        
        log_info(
            "Streak validation complete",
            total_checked=len(habits),
            streaks_reset=reset_count
        )
        
        return {
            'statusCode': 200,
            'body': {
                'message': 'Streak validation complete',
                'habits_checked': len(habits),
                'streaks_reset': reset_count
            }
        }
        
    except Exception as e:
        log_error("Streak validation failed", e)
        return {
            'statusCode': 500,
            'body': {'error': str(e)}
        }
