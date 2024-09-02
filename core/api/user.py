from fastapi import APIRouter, HTTPException, Depends
from core.models.user import (
    UserCreateRequest,
    UserResponse,
    UserLoginRequest,
)
from sqlmodel import Session, select
from core.db.database import get_session
from hashlib import sha256
from core.models.db import User
import uuid

router = APIRouter()


# Helper function to hash the password
def hash_password(password: str) -> str:
    return sha256(password.encode()).hexdigest()

# Endpoint to register a new user
@router.post("/v1/users", response_model=UserResponse)
async def register_user(user_request: UserCreateRequest, session: Session = Depends(get_session)):
    # Hash the password
    password_hash = hash_password(user_request.password)

    # Check if the email already exists
    statement = select(User).where(User.email == user_request.email)
    existing_user = session.exec(statement).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Generate a unique user_id
    user_id = str(uuid.uuid4())

    # Create the new user and store it in the database
    new_user = User(
        user_id=user_id,
        email=user_request.email,
        password_hash=password_hash,
        language=user_request.language
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return UserResponse(user_id=new_user.user_id, email=new_user.email, language=new_user.language)

# Endpoint to create a session (login)
@router.post("/v1/sessions", response_model=UserResponse)
async def create_session(user_request: UserLoginRequest, session: Session = Depends(get_session)):
    # Retrieve user data from the database
    statement = select(User).where(User.email == user_request.email)
    user = session.exec(statement).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Verify the password
    if user.password_hash != hash_password(user_request.password):
        raise HTTPException(status_code=401, detail="Invalid password")

    return UserResponse(user_id=user.user_id, email=user.email, language=user.language)