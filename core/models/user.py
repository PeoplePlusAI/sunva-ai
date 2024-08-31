from pydantic import BaseModel

class UserCreateRequest(BaseModel):
    user_id: str
    password: str
    language: str

class UserResponse(BaseModel):
    user_id: str
    language: str

class UserLoginRequest(BaseModel):
    user_id: str
    password: str

class LanguageUpdateRequest(BaseModel):
    language: str
