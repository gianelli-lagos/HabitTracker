from sqlalchemy.orm import Session
from models.notification import Notification
from datetime import datetime

def create_notification(
    db: Session,
    user_id: int,
    type: str,
    title: str,
    message: str,
    data: dict = None
):
    """
    Create a notification
    Used by: Backend endpoints AND Lambda functions
    """
    notification = Notification(
        user_id=user_id,
        type=type,
        title=title,
        message=message,
        data=data
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification

def get_user_notifications(
    db: Session,
    user_id: int,
    unread_only: bool = False,
    limit: int = 20
):
    """Get user's notifications"""
    query = db.query(Notification).filter(Notification.user_id == user_id)
    
    if unread_only:
        query = query.filter(Notification.is_read == False)
    
    return query.order_by(Notification.created_at.desc()).limit(limit).all()

def mark_notification_read(db: Session, notification_id: int):
    """Mark notification as read"""
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if notification:
        notification.is_read = True
        notification.read_at = datetime.utcnow()
        db.commit()
    return notification

def mark_all_read(db: Session, user_id: int):
    """Mark all user's notifications as read"""
    db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.is_read == False
    ).update({"is_read": True, "read_at": datetime.utcnow()})
    db.commit()

def delete_notification(db, notification_id):
    """
    Delete a notification
    """
    notification = db.query(Notification).filter(
        Notification.id == notification_id
    ).first()
    
    if notification:
        db.delete(notification)
        db.commit()
        return True
    
    return False