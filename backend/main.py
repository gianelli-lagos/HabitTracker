from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from database import engine, Base
from routers import auth, notifications, habits, events
import time

# Load environment variables from .env file
load_dotenv()

# Import all models so Base.metadata.create_all() knows about them
from models.user import User
from models.notification import Notification
from models import user, notification, habit, event

# Wait for database to be ready
for i in range(10):
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
        break
    except Exception as e:
        print(f"Database not ready, retrying in 3 seconds... ({i+1}/10)")
        print(f"Error: {e}")
        time.sleep(3)

app = FastAPI(title="Habit Tracker API")

# CORS allows to connect REACT w/ backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React default
        "http://localhost:5173",  # Vite default
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router)
app.include_router(notifications.router)
app.include_router(habits.router)
app.include_router(events.router)

@app.get("/")
def root():
    return {"message": "Habit Tracker API is running"}

@app.get("/health")
def health():
    return {"status": "healthy"}