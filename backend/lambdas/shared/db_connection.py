import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def get_db_session():
    """
    Get database session for Lambda functions
    Works for both local and AWS (uses environment variable)
    """
    # Try environment variable first, then use local default
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:password@localhost:5434/habittracker"  # Local default
    )
    
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=3600
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    return SessionLocal()