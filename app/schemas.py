from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    password: str
    email: EmailStr


class UserLogin(BaseModel):
    password: str
    email: EmailStr


class UserOut(BaseModel):
    email: EmailStr