from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from models.social import FriendRequest, FriendRequestStatus
from models.user import User
from database import get_db
from routers.auth import oauth2_scheme, get_current_user

router = APIRouter(prefix="/social", tags=["social"])

# Request/Response schemas
class FriendRequestCreate(BaseModel):
    username: str  # Username of person to send request to

class FriendRequestResponse(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    status: str
    created_at: str
    
    class Config:
        from_attributes = True

class UserBriefResponse(BaseModel):
    id: int
    username: str
    profile_picture_url: str | None = None

# Endpoint 0: Search users by username
@router.get("/search")
async def search_users(
    q: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Search for users by username. Query parameter 'q' is required."""
    if not q or len(q) < 1:
        return []
    
    # Search for users matching the query, excluding current user
    users = db.query(User).filter(
        User.username.ilike(f"%{q}%"),
        User.id != current_user.id
    ).limit(20).all()  # Limit to 20 results
    
    result = []
    for user in users:
        result.append({
            "id": user.id,
            "username": user.username,
            "profile_picture_url": user.profile_picture_url
        })
    
    return result

# Endpoint 1: Send friend request
@router.post("/friend-request")
async def send_friend_request(
    request: FriendRequestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if receiver exists
    receiver = db.query(User).filter(User.username == request.username).first()
    if not receiver:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Can't send request to yourself
    if receiver.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot send request to yourself")
    
    # Check if request already exists
    existing = db.query(FriendRequest).filter(
        FriendRequest.sender_id == current_user.id,
        FriendRequest.receiver_id == receiver.id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Friend request already exists")
    
    # Create and save request
    friend_request = FriendRequest(
        sender_id=current_user.id,
        receiver_id=receiver.id,
        status=FriendRequestStatus.PENDING
    )
    db.add(friend_request)
    db.commit()
    db.refresh(friend_request)
    
    return {"message": "Friend request sent", "request_id": friend_request.id}

# Endpoint 2: Get pending friend requests
@router.get("/pending-requests")
async def get_pending_requests(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    pending = db.query(FriendRequest).filter(
        FriendRequest.receiver_id == current_user.id,
        FriendRequest.status == FriendRequestStatus.PENDING
    ).all()
    
    result = []
    for req in pending:
        result.append({
            "id": req.id,
            "sender": {
                "id": req.sender.id,
                "username": req.sender.username,
                "profile_picture_url": req.sender.profile_picture_url
            },
            "created_at": req.created_at.isoformat()
        })
    
    return result

# Endpoint 3: Accept friend request
@router.post("/friend-request/{request_id}/accept")
async def accept_friend_request(
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    friend_request = db.query(FriendRequest).filter(
        FriendRequest.id == request_id,
        FriendRequest.receiver_id == current_user.id
    ).first()
    
    if not friend_request:
        raise HTTPException(status_code=404, detail="Friend request not found")
    
    friend_request.status = FriendRequestStatus.ACCEPTED
    db.commit()
    
    return {"message": "Friend request accepted"}

# Endpoint 4: Reject/decline friend request
@router.post("/friend-request/{request_id}/reject")
async def reject_friend_request(
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    friend_request = db.query(FriendRequest).filter(
        FriendRequest.id == request_id,
        FriendRequest.receiver_id == current_user.id
    ).first()
    
    if not friend_request:
        raise HTTPException(status_code=404, detail="Friend request not found")
    
    friend_request.status = FriendRequestStatus.DECLINED
    db.commit()
    
    return {"message": "Friend request declined"}

# Endpoint 5: Get friends list (accepted requests)
@router.get("/friends")
async def get_friends(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Get accepted requests where current_user is sender or receiver
    sent_accepted = db.query(FriendRequest).filter(
        FriendRequest.sender_id == current_user.id,
        FriendRequest.status == FriendRequestStatus.ACCEPTED
    ).all()
    
    received_accepted = db.query(FriendRequest).filter(
        FriendRequest.receiver_id == current_user.id,
        FriendRequest.status == FriendRequestStatus.ACCEPTED
    ).all()
    
    friends = []
    
    # From sent requests, get the receivers
    for req in sent_accepted:
        friends.append({
            "id": req.receiver.id,
            "username": req.receiver.username,
            "profile_picture_url": req.receiver.profile_picture_url
        })
    
    # From received requests, get the senders
    for req in received_accepted:
        friends.append({
            "id": req.sender.id,
            "username": req.sender.username,
            "profile_picture_url": req.sender.profile_picture_url
        })
    
    return friends
