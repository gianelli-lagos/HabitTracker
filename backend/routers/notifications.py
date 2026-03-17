from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from routers.auth import get_current_user
from models.user import User
from services.notification_service import (
    create_notification,
    get_user_notifications,
    mark_notification_read,
    mark_all_read,
    delete_notification
)

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.get("")
def get_notifications(
    unread_only: bool = False,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's notifications"""
    notifications = get_user_notifications(db, current_user.id, unread_only, limit)
    return notifications

@router.put("/{notification_id}/read")
def mark_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark notification as read"""
    notification = mark_notification_read(db, notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    # Check ownership
    if notification.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return {"message": "Notification marked as read"}

@router.put("/read-all")
def mark_all_notifications_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark all notifications as read"""
    mark_all_read(db, current_user.id)
    return {"message": "All notifications marked as read"}

@router.get("/unread-count")
def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get count of unread notifications"""
    from models.notification import Notification
    count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).count()
    return {"count": count}

@router.delete("/{notification_id}")
def remove_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a notification"""
    notification = delete_notification(db, notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    # Check ownership
    if notification.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return {"message": "Notification deleted"}

# TEST ENDPOINT (for development)
@router.post("/test")
def create_test_notification(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a test notification"""
    notification = create_notification(
        db=db,
        user_id=current_user.id,
        type='test',
        title='🎉 Test Notification',
        message='This is a test notification from the system!',
        data={'test': True}
    )
    return notification