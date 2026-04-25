import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.db_connection import get_db_session
from shared.logger import log_info, log_error

def lambda_handler(event, context):
    """
    Test Lambda - Creates a test notification
    Use this to verify Lambda can connect to RDS
    """
    log_info("Starting test notification Lambda")
    
    try:
        db = get_db_session()
        
        # Import models
        from models.notification import Notification
        
        # Create test notification
        notification = Notification(
            user_id=1,
            type='test',
            title='🚀 Lambda Test',
            message='Lambda function successfully connected to database!',
            data={'lambda_name': 'test_notification', 'success': True}
        )
        
        db.add(notification)
        db.commit()
        
        log_info("Test notification created", notification_id=notification.id)
        
        db.close()
        
        return {
            'statusCode': 200,
            'body': {
                'message': 'Test notification created successfully',
                'notification_id': notification.id
            }
        }
        
    except Exception as e:
        log_error("Lambda execution failed", e)
        return {
            'statusCode': 500,
            'body': {'error': str(e)}
        }