"""
Shared test fixtures for all tests
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base
from models.user import User
from models.habit import Habit
from models.notification import Notification
from models.social import FriendRequest, FriendRequestStatus
import bcrypt

# Test database (in-memory SQLite)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    """Create fresh test database for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_user(db):
    """Create test user"""
    hashed_password = bcrypt.hashpw(b"test123", bcrypt.gensalt()).decode('utf-8')
    user = User(
        username="testuser",
        hashed_password=hashed_password
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def test_user2(db):
    """Create second test user"""
    hashed_password = bcrypt.hashpw(b"test123", bcrypt.gensalt()).decode('utf-8')
    user = User(
        username="testuser2",
        hashed_password=hashed_password
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def test_user3(db):
    """Create third test user"""
    hashed_password = bcrypt.hashpw(b"test123", bcrypt.gensalt()).decode('utf-8')
    user = User(
        username="testuser3",
        hashed_password=hashed_password
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def test_habit(db, test_user):
    """Create test habit"""
    habit = Habit(
        user_id=test_user.id,
        name="Meditation",
        current_streak=5,
        longest_streak=7,
        is_active=True
    )
    db.add(habit)
    db.commit()
    db.refresh(habit)
    return habit