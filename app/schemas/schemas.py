from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    password: str
    username: str
    email: EmailStr



class UserLogin(BaseModel):
    password: str
    email: EmailStr


class UserOut(BaseModel):
    email: EmailStr


class TokenOut(BaseModel):
    user: EmailStr
    token_type: str = "bearer"
    access_token: str