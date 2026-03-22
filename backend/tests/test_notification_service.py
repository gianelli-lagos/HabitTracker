"""
Unit tests for notification service
Run: pytest tests/test_notification_service.py -v
"""
import pytest
from services.notification_service import (
    create_notification,
    get_user_notifications,
    mark_notification_read,
    mark_all_read,
    delete_notification
)

def test_create_notification(db, test_user):
    """Test creating a notification"""
    notification = create_notification(
        db=db,
        user_id=test_user.id,
        type='test',
        title='Test Notification',
        message='This is a test',
        data={'test': True}
    )
    
    assert notification.id is not None
    assert notification.user_id == test_user.id
    assert notification.type == 'test'
    assert notification.title == 'Test Notification'
    assert notification.is_read == False
    assert notification.data == {'test': True}

def test_get_user_notifications(db, test_user):
    """Test getting user's notifications"""
    # Create 3 notifications
    for i in range(3):
        create_notification(
            db=db,
            user_id=test_user.id,
            type='test',
            title=f'Notification {i}',
            message='Test message'
        )
    
    notifications = get_user_notifications(db, test_user.id)
    assert len(notifications) == 3
    # Notifications exist (don't check order, SQLite vs PostgreSQL differ)
    titles = [n.title for n in notifications]
    assert 'Notification 0' in titles
    assert 'Notification 1' in titles
    assert 'Notification 2' in titles

def test_mark_notification_read(db, test_user):
    """Test marking notification as read"""
    notification = create_notification(
        db=db,
        user_id=test_user.id,
        type='test',
        title='Test',
        message='Test'
    )
    
    assert notification.is_read == False
    assert notification.read_at is None
    
    marked = mark_notification_read(db, notification.id)
    
    assert marked.is_read == True
    assert marked.read_at is not None

def test_get_unread_only(db, test_user):
    """Test getting only unread notifications"""
    notif1 = create_notification(db, test_user.id, 'test', 'Test 1', 'Message 1')
    notif2 = create_notification(db, test_user.id, 'test', 'Test 2', 'Message 2')
    
    mark_notification_read(db, notif1.id)
    
    unread = get_user_notifications(db, test_user.id, unread_only=True)
    
    assert len(unread) == 1
    assert unread[0].id == notif2.id

def test_mark_all_read(db, test_user):
    """Test marking all notifications as read"""
    for i in range(3):
        create_notification(db, test_user.id, 'test', f'Test {i}', 'Message')
    
    mark_all_read(db, test_user.id)
    
    unread = get_user_notifications(db, test_user.id, unread_only=True)
    assert len(unread) == 0

def test_delete_notification(db, test_user):
    """Test deleting a notification"""
    notification = create_notification(db, test_user.id, 'test', 'Test', 'Message')
    notif_id = notification.id
    
    result = delete_notification(db, notif_id)
    
    # Check that notification is deleted
    from models.notification import Notification
    deleted = db.query(Notification).filter_by(id=notif_id).first()
    assert deleted is None

def test_notification_limit(db, test_user):
    """Test notification limit parameter"""
    for i in range(10):
        create_notification(db, test_user.id, 'test', f'Test {i}', 'Message')
    
    limited = get_user_notifications(db, test_user.id, limit=5)
    assert len(limited) == 5