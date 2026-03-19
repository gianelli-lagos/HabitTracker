import sys
import os
from datetime import datetime, timedelta

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
    Runs Sunday 8:00 PM UTC
    
    Generates weekly summary for each user
    Shows: habits completed, completion rate, longest streak
    
    For testing: pass event = {"test_user_id": 3} to only send to one user
    """
    log_info("Starting weekly summary generation")
    
    try:
        db = get_db_session()
        now = datetime.now()
        week_ago = now - timedelta(days=7)
        
        summary_count = 0
        
        # Check if this is a test run for specific user
        test_user_id = event.get('test_user_id') if event else None
        
        if test_user_id:
            # TEST MODE: Only send to specific user
            log_info(f"TEST MODE: Sending summary only to user {test_user_id}")
            users = db.query(User).filter(User.id == test_user_id).all()
        else:
            # PRODUCTION MODE: Send to all users
            users = db.query(User).all()
        
        log_info(f"Generating summaries for {len(users)} users")
        
        for user in users:
            # Calculate habits completed this week
            habits_completed = db.query(HabitLog).filter(
                HabitLog.user_id == user.id,
                HabitLog.date >= week_ago.date()
            ).count()
            
            # Calculate total expected (active habits × 7 days)
            active_habits = db.query(Habit).filter(
                Habit.user_id == user.id,
                Habit.is_active == True
            ).count()
            
            habits_expected = active_habits * 7
            
            # Calculate completion rate
            if habits_expected > 0:
                completion_rate = int((habits_completed / habits_expected) * 100)
            else:
                completion_rate = 0
            
            # Find longest active streak
            habits = db.query(Habit).filter(Habit.user_id == user.id).all()
            longest_streak = max([h.current_streak for h in habits]) if habits else 0
            
            # Create motivational message
            if completion_rate >= 80:
                emoji = "🎉"
                msg = f"Amazing week! You completed {habits_completed}/{habits_expected} habits ({completion_rate}%)."
            elif completion_rate >= 50:
                emoji = "💪"
                msg = f"Good progress! You completed {habits_completed}/{habits_expected} habits ({completion_rate}%)."
            else:
                emoji = "🌱"
                msg = f"New week, fresh start! Last week: {habits_completed}/{habits_expected} habits ({completion_rate}%)."
            
            if longest_streak > 0:
                msg += f" Longest streak: {longest_streak} days!"
            
            # Create summary notification
            create_notification(
                db=db,
                user_id=user.id,
                type='weekly_summary',
                title=f'{emoji} Your Week in Review',
                message=msg,
                data={
                    'habits_completed': habits_completed,
                    'habits_expected': habits_expected,
                    'completion_rate': completion_rate,
                    'longest_streak': longest_streak,
                    'week_start': week_ago.isoformat(),
                    'week_end': now.isoformat(),
                    'test_mode': test_user_id is not None
                }
            )
            
            summary_count += 1
            
            log_info(
                "Summary created",
                user_id=user.id,
                completion_rate=completion_rate
            )
        
        db.close()
        
        log_info(
            "Weekly summaries complete",
            summaries_sent=summary_count,
            test_mode=test_user_id is not None
        )
        
        return {
            'statusCode': 200,
            'body': {
                'message': 'Weekly summaries sent',
                'summaries_sent': summary_count,
                'test_mode': test_user_id is not None
            }
        }
        
    except Exception as e:
        log_error("Weekly summary failed", e)
        return {
            'statusCode': 500,
            'body': {'error': str(e)}
        }