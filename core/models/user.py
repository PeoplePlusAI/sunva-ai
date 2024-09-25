from pydantic import BaseModel

class UserCreateRequest(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    user_id: str
    email: str

class UserLoginRequest(BaseModel):
    email: str
    password: str
