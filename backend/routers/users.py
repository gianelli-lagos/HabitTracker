from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from routers.auth import oauth2_scheme, get_current_user
from services.s3_service import upload_profile_picture, delete_profile_picture, get_profile_picture_url
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        logger.info(f"Starting profile picture upload for user {current_user.id}")
        logger.info(f"File: {file.filename}, Size: {len(file.file.read()) if hasattr(file.file, 'read') else 'unknown'}")
        
        # Read file content
        contents = await file.read()
        logger.info(f"File read successfully: {len(contents)} bytes")
        
        # Delete old profile picture if exists
        logger.info(f"Attempting to delete old profile picture for user {current_user.id}")
        delete_profile_picture(current_user.id)
        
        # Upload to S3 (returns presigned URL for immediate use)
        logger.info(f"Uploading to S3 for user {current_user.id}")
        presigned_url = upload_profile_picture(
            file_content=contents,
            user_id=current_user.id,
            filename=file.filename
        )
        logger.info(f"S3 upload successful. Presigned URL: {presigned_url[:50]}...")
        
        # Store a marker that profile picture exists
        # Generate fresh presigned URL on-demand when needed
        current_user.profile_picture_url = "s3"
        db.commit()
        logger.info(f"Database updated for user {current_user.id}")
        
        return {
            "profile_picture_url": presigned_url,
            "message": "Profile picture uploaded successfully to S3"
        }
    except Exception as e:
        logger.error(f"Error uploading profile picture: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
