from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
import re


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field(..., min_length=2, max_length=100)

    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError("Логін: лише латинські літери, цифри та _")
        return v

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v):
        if re.search(r"[<>&\"']", v):
            raise ValueError("Ім’я не може містити < > & \"")
        return v.strip()

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v):
        if not re.search(r"[A-Z]", v):
            raise ValueError("Потрібна хоча б одна велика літера")
        if not re.search(r"[a-z]", v):
            raise ValueError("Потрібна хоча б одна мала літера")
        if not re.search(r"\d", v):
            raise ValueError("Потрібна хоча б одна цифра")
        return v


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefreshRequest(BaseModel):
    refresh_token: str


class UserInfo(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    role: str

    model_config = {"from_attributes": True}