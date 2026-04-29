from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from routers.auth import oauth2_scheme, get_current_user
from services.s3_service import upload_profile_picture, delete_profile_picture, get_profile_picture_url

router = APIRouter(prefix="/users", tags=["users"])


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
    
    # Get fresh presigned URL if profile picture exists
    profile_picture_url = None
    if user.profile_picture_url:
        profile_picture_url = get_profile_picture_url(user.id)
    
    return {
        "id": user.id,
        "username": user.username,
        "profile_picture_url": profile_picture_url
    }


@router.post("/upload-profile-picture")
async def upload_profile_picture_endpoint(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload profile picture for the current user to S3"""
    try:
        # Read file content
        contents = await file.read()
        
        # Delete old profile picture if exists
        delete_profile_picture(current_user.id)
        
        # Upload to S3 (returns presigned URL for immediate use)
        presigned_url = upload_profile_picture(
            file_content=contents,
            user_id=current_user.id,
            filename=file.filename
        )
        
        # Store a marker that profile picture exists
        # Generate fresh presigned URL on-demand when needed
        current_user.profile_picture_url = "s3"
        db.commit()
        
        return {"profile_picture_url": presigned_url, "message": "Profile picture uploaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
