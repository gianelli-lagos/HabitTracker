from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from database import engine, Base
from routers import auth, notifications, habits, events, users, social
import os

load_dotenv()

# Models (ensure metadata is registered)
from models.user import User
from models.notification import Notification
from models.social import FriendRequest
from models import user, notification, habit, event


app = FastAPI(title="Habit Tracker API")


# ----------------------------
# HEALTH FIRST (IMPORTANT)
# ----------------------------
@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def root():
    return {"message": "Welcome to HabitTracker API"}


# ----------------------------
# DB INIT (SAFE STARTUP)
# ----------------------------
@app.on_event("startup")
def startup():
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"❌ DB init failed (non-fatal): {e}")


# ----------------------------
# STATIC FILES
# ----------------------------
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


# ----------------------------
# CORS
# ----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----------------------------
# ROUTERS
# ----------------------------
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(notifications.router)
app.include_router(habits.router)
app.include_router(events.router)
app.include_router(social.router)