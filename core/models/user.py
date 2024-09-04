from pydantic import BaseModel

class UserCreateRequest(BaseModel):
    email: str
    password: str
    language: str

class UserResponse(BaseModel):
    user_id: str
    email: str
    language: str

class UserLoginRequest(BaseModel):
    email: str
    password: str
