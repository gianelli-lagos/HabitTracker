from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

# Represents an application user, storing authentication details and
# linking to related data such as notifications.
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    notifications = relationship("Notification", back_populates="user")
    habits = relationship("Habit", back_populates="user")
    created_events = relationship("Event", back_populates="creator")