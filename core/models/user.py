from pydantic import BaseModel

class UserCreateRequest(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    user_id: str
    email: str
    access_token: str
    message: Optional[str] = None

class UserLoginRequest(BaseModel):
    email: str
    password: str
