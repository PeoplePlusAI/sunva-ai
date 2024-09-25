from fastapi import APIRouter, HTTPException, Depends, Header, Response, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
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
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv(
    "ops/.env"
)

router = APIRouter()
security = HTTPBearer()

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("No SECRET_KEY set for JWT. Please set it in the environment variables.")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Helper function to hash the password
def hash_password(password: str) -> str:
    return sha256(password.encode()).hexdigest()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Endpoint to register a new user
@router.post("/user/register", response_model=UserResponse)
async def register_user(user_request: UserCreateRequest, response: Response, session: Session = Depends(get_session)):
    # Hash the password
    password_hash = hash_password(user_request.password)

    # Check if the email already exists
    statement = select(User).where(User.email == user_request.email)
    existing_user = await session.execute(statement)
    existing_user = existing_user.scalars().first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Generate a unique user_id
    user_id = str(uuid.uuid4())

    # Create the new user and store it in the database
    new_user = User(
        user_id=user_id,
        email=user_request.email,
        password_hash=password_hash
    )
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    # Create access token
    access_token = create_access_token(
        data={"sub": new_user.email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    # Set the access token as a secure HTTP-only cookie
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


    return UserResponse(user_id=new_user.user_id, email=new_user.email, access_token=access_token)

# Endpoint to create a session (login)
@router.post("/user/login", response_model=UserResponse)
async def create_session(
    user_request: UserLoginRequest,
    response: Response, 
    session: Session = Depends(get_session),
    authorization: Optional[str] = Header(None)
):
    # Check if the user is already logged in
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            # Token is valid, user is already logged in
            return UserResponse(
                user_id=payload.get("user_id"),
                email=payload.get("sub"),
                access_token=token,
                message="Already logged in"
            )
        except JWTError:
            # Token is invalid, proceed with login
            pass

    # Retrieve user data from the database
    statement = select(User).where(User.email == user_request.email)
    user = await session.execute(statement)
    user = user.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Verify the password
    if user.password_hash != hash_password(user_request.password):
        raise HTTPException(status_code=401, detail="Invalid password")

    # Create access token
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.user_id},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

    return UserResponse(user_id=user.user_id, email=user.email, access_token=access_token)

# Endpoint to delete a session (logout)
@router.post("/user/logout")
async def logout(response: Response, credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # In a real-world scenario, you might want to blacklist this token
        # or remove it from a token store

        response.delete_cookie(key="access_token")
        return {"message": "Successfully logged out"}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Add this new endpoint after the existing ones
@router.get("/user/verify", response_model=UserResponse)
async def verify_token(request: Request, credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    logger.info(f"Received request headers: {request.headers}")
    
    if not credentials:
        logger.warning("No credentials provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is missing"
        )
    
    token = credentials.credentials
    logger.info(f"Received token: {token[:10]}...")  # Log first 10 characters of token for debugging
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        user_id = payload.get("user_id")
        
        logger.info(f"Decoded payload: email={email}, user_id={user_id}")
        
        if email is None or user_id is None:
            logger.warning("Invalid token payload")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        return UserResponse(user_id=user_id, email=email, access_token=token)
    except JWTError as e:
        logger.error(f"JWT decoding error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )