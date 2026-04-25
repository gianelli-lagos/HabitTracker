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
    Runs at 9:00 AM EDT daily
    
    Finds habits that haven't been logged today
    Creates reminder notifications
    """
    log_info("Starting daily habit reminders")
    
    try:
        db = get_db_session()
        today = date.today()
        reminder_count = 0
        
        # Get all active habits
        habits = db.query(Habit).filter(Habit.is_active == True).all()
        
        log_info(f"Checking {len(habits)} active habits")
        
        for habit in habits:
            # Check if already logged today
            logged_today = db.query(HabitLog).filter(
                HabitLog.habit_id == habit.id,
                HabitLog.date == today
            ).first()
            
            if not logged_today:
                # Not logged yet - send reminder
                reminder_count += 1
                
                # Create motivational message with current streak
                if habit.current_streak > 0:
                    message = f"You haven't logged {habit.name} yet today. Keep your {habit.current_streak}-day streak going!"
                else:
                    message = f"Don't forget to log {habit.name} today!"
                
                create_notification(
                    db=db,
                    user_id=habit.user_id,
                    type='habit_reminder',
                    title=f'Time for {habit.name}! 🌱',
                    message=message,
                    data={
                        'habit_id': habit.id,
                        'habit_name': habit.name,
                        'current_streak': habit.current_streak
                    }
                )
                
                log_info(
                    "Reminder created",
                    habit_id=habit.id,
                    user_id=habit.user_id
                )
        
        db.close()
        
        log_info(
            "Daily reminders complete",
            total_habits=len(habits),
            reminders_sent=reminder_count
        )
        
        return {
            'statusCode': 200,
            'body': {
                'message': 'Daily reminders sent',
                'habits_checked': len(habits),
                'reminders_sent': reminder_count
            }
        }
        
    except Exception as e:
        log_error("Daily reminders failed", e)
        return {
            'statusCode': 500,
            'body': {'error': str(e)}
        }
    