from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from routers.auth import oauth2_scheme, get_current_user
import os
import shutil

router = APIRouter(prefix="/users", tags=["users"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.get("/{user_id}")
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user profile by ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return {"id": user.id, "username": user.username}


@router.post("/upload-profile-picture")
async def upload_profile_picture(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload profile picture for the current user"""
    try:
        # Save file
        filename = f"{current_user.id}_{file.filename}"
        filepath = os.path.join(UPLOAD_DIR, filename)
        
        with open(filepath, "wb") as buffer:
            contents = await file.read()
            buffer.write(contents)
        
        # Update user record
        file_url = f"/uploads/{filename}"
        current_user.profile_picture_url = file_url
        db.commit()
        
        return {"profile_picture_url": file_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
