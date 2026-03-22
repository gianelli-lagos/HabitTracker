"""
Integration tests for Lambda functions
Run: pytest tests/test_lambdas.py -v
"""
import pytest
import sys
import os

# Add paths
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)
sys.path.insert(0, os.path.join(backend_dir, 'lambdas'))

from models.notification import Notification
from models.habit import HabitLog

# Import Lambda handlers
from lambdas.test_notification.handler import lambda_handler as test_handler
from lambdas.daily_reminders.handler import lambda_handler as reminders_handler
from lambdas.midnight_streak_validator.handler import lambda_handler as validator_handler
from lambdas.weekly_summary.handler import lambda_handler as summary_handler


def test_test_notification_lambda_executes(db, test_user):
    """Test that test_notification Lambda executes successfully"""
    result = test_handler({}, {})
    
    assert result['statusCode'] == 200
    assert 'notification_id' in result['body']
    assert result['body']['message'] == 'Test notification created successfully'


def test_daily_reminders_lambda_executes(db, test_user, test_habit):
    """Test that daily_reminders Lambda executes successfully"""
    result = reminders_handler({}, {})
    
    assert result['statusCode'] == 200
    assert 'reminders_sent' in result['body']
    assert isinstance(result['body']['reminders_sent'], int)


def test_midnight_validator_lambda_executes(db, test_user, test_habit):
    """Test that midnight_streak_validator Lambda executes successfully"""
    result = validator_handler({}, {})
    
    assert result['statusCode'] == 200
    assert 'streaks_reset' in result['body']
    assert isinstance(result['body']['streaks_reset'], int)


def test_weekly_summary_lambda_executes(db, test_user):
    """Test that weekly_summary Lambda executes successfully"""
    result = summary_handler({}, {})
    
    assert result['statusCode'] == 200
    assert 'summaries_sent' in result['body']
    assert isinstance(result['body']['summaries_sent'], int)