from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, field_validator


# دریافت اطلاعات ثبت نام
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=72)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 8 or len(v) > 72:
            raise ValueError("Password must be between 8 and 72 chars long")
        return v


class UserRead(BaseModel):
    id: UUID
    email: EmailStr
    is_verified: bool
    created_at: datetime | None = None

    model_config = {
        "from_attributes": True
    }


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int | None = None


class TokenData(BaseModel):
    email: EmailStr | None = None