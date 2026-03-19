from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

# Represents a user notification in the system, storing message content,
# type, metadata, and read status for tracking and delivery purposes.
class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(50), nullable=False)
    # Types: 'habit_reminder', 'milestone', 'event_1day', 'event_1hour', 'weekly_summary', 'streak_broken'
    title = Column(String(200), nullable=False)
    message = Column(String, nullable=False)
    data = Column(JSON)  # Extra info: habit_id, event_id, streak_count, etc.
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    read_at = Column(DateTime)
    
    # Relationship to User
    user = relationship("User", back_populates="notifications")