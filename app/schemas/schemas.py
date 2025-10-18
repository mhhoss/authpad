from datetime import datetime
from pydantic import BaseModel, EmailStr


# دریافت اطلاعات ثبت نام و 
class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserRead(BaseModel):
    id: str
    email: EmailStr
    is_verified: bool
    created_at: datetime | None = None

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    email: EmailStr | None = None