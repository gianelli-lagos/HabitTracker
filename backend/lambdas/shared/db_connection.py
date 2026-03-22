import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def get_db_session():
    """Create and return a new database session (useful for Lambda or stateless apps)."""

    # Get the database connection string from environment variables
    database_url = os.getenv("DATABASE_URL")

    # Fail early if the connection string is missing
    if not database_url:
        raise ValueError("DATABASE_URL environment variable not set")
    
    # Initialize the database engine (handles connections under the hood)
    engine = create_engine(database_url)

    # Create a session factory bound to this engine
    SessionLocal = sessionmaker(bind=engine)

    # Return a new session instance (caller should close it after use)
    return SessionLocal()