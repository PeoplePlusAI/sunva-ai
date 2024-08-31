from fastapi import APIRouter, HTTPException, Depends
from core.models.user import (
    UserCreateRequest,
    UserResponse,
    UserLoginRequest,
    LanguageUpdateRequest
)
from sqlmodel import Session, select
from core.db.database import get_session
from hashlib import sha256
from core.models.db import User

router = APIRouter()


# Helper function to hash the password
def hash_password(password: str) -> str:
    return sha256(password.encode()).hexdigest()

# Endpoint to register a new user
@router.post("/users", response_model=UserResponse)
async def register_user(user_request: UserCreateRequest, session: Session = Depends(get_session)):
    # Hash the password
    password_hash = hash_password(user_request.password)

    # Check if the user already exists
    statement = select(User).where(User.user_id == user_request.user_id)
    existing_user = session.exec(statement).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User ID already exists")

    # Create the new user and store it in the database
    new_user = User(
        user_id=user_request.user_id,
        password_hash=password_hash,
        language=user_request.language
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return UserResponse(user_id=new_user.user_id, language=new_user.language)

# Endpoint to create a session (login)
@router.post("/sessions", response_model=UserResponse)  # Consider returning a token instead
async def create_session(user_request: UserLoginRequest, session: Session = Depends(get_session)):
    # Retrieve user data from the database
    statement = select(User).where(User.user_id == user_request.user_id)
    user = session.exec(statement).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Verify the password
    if user.password_hash != hash_password(user_request.password):
        raise HTTPException(status_code=401, detail="Invalid password")

    # Here, consider generating and returning a token for stateless authentication
    return UserResponse(user_id=user.user_id, language=user.language)

# RESTful endpoint to update the user's language
@router.put("/users/{user_id}/language", response_model=UserResponse)
async def update_user_language(user_id: str, language_update: LanguageUpdateRequest, session: Session = Depends(get_session)):
    # Retrieve the user from the database
    statement = select(User).where(User.user_id == user_id)
    user = session.exec(statement).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update the language
    user.language = language_update.language
    session.add(user)
    session.commit()
    session.refresh(user)

    return UserResponse(user_id=user.user_id, language=user.language)