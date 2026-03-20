from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os

from database import get_db
from models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])

password_hashing = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
#creating and verifying unque user tokens with JWT
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

def hash_password(password: str) -> str:
    return password_hashing.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hashing.verify(plain_password, hashed_password)

#data for incoming requests
#used Pydantic because it automatically validates incoming data
#keeps code cleaner
class UserRegister(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

#create JWT token that lasts for 30 minutes
def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    #ensures access to server
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#reads every token on every request
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        #start reading token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        #get username stored in token
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    #looks up username in database and returns if real user
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user
#REGISTER LOGIC
@router.post("/register", response_model=UserResponse, status_code=201)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    #check if user already taken
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")
    
    #hash password and save registered user
    registered_user = User(
        username=user_data.username,
        hashed_password=hash_password(user_data.password),
    )
    db.add(registered_user)
    db.commit()
    db.refresh(registered_user)
    return registered_user
#LOGIN LOGIC
@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    #find registered user by username
    user = db.query(User).filter(User.username == form_data.username).first()
    
    #check if user exists and if password is correct
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    
    #create and return token
    access_token = create_access_token(data={"sub": user.username})
    #bearer is user carrying token
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/profile", response_model=UserResponse)
def return_profile(current_user: User = Depends(get_current_user)):
    # Returns the currently logged in user
    return current_user