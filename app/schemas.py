from pydantic import BaseModel, EmailStr


class SignupRequest(BaseModel):
    email: EmailStr
    username: str
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    username: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str