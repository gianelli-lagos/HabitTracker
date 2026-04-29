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
from models.user import User
from models.habit import Habit, HabitLog
from services.notification_service import create_notification


def lambda_handler(event, context):
    """
    Daily Habit Reminder Lambda
    Runs at 9:00 AM EDT
    Sends reminder if a habit has NOT been logged today
    """

    log_info('Starting daily habit reminders')

    try:
        db = get_db_session()
        today = date.today()

        reminder_count = 0
        user_count = 0

        # Get all users
        users = db.query(User).all()

        log_info(f'Total users found: {len(users)}')

        for user in users:
            user_count += 1

            # Get habits per user
            habits = db.query(Habit).filter(
                Habit.user_id == user.id
            ).all()

            log_info(f'User {user.id} has {len(habits)} habits')

            for habit in habits:

                # Check if habit already logged today
                logged_today = db.query(HabitLog).filter(
                    HabitLog.habit_id == habit.id,
                    HabitLog.date == today
                ).first()

                if logged_today:
                    log_info(f'Skipping habit {habit.id} (already logged today)')
                    continue

                # Send reminder
                reminder_count += 1

                if habit.current_streak > 0:
                    message = (
                        f"You haven't logged {habit.name} yet today. "
                        f"Keep your {habit.current_streak}-day streak going!"
                    )
                else:
                    message = f"Don't forget to log {habit.name} today!"

                create_notification(
                    db=db,
                    user_id=user.id,
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
                    'Reminder created',
                    user_id=user.id,
                    habit_id=habit.id
                )

        db.commit()
        db.close()

        log_info(
            'Daily reminders complete',
            users_checked=user_count,
            reminders_sent=reminder_count
        )

        return {
            'statusCode': 200,
            'body': {
                'message': 'Daily reminders sent',
                'users_checked': user_count,
                'reminders_sent': reminder_count
            }
        }

    except Exception as e:
        log_error('Daily reminders failed', e)
        return {
            'statusCode': 500,
            'body': {'error': str(e)}
        }