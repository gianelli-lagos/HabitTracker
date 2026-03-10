from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import auth
import time
# Wait for database to be ready
for i in range(10):
    try:
        Base.metadata.create_all(bind=engine)
        break
    except Exception:
        print(f"Database not ready, retrying in 3 seconds... ({i+1}/10)")
        time.sleep(3)
app = FastAPI(title="Habit Tracker API")
#CORS allows to connect REACT w/ backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
#register routers
app.include_router(auth.router)