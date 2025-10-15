from fastapi import APIRouter, Depends, HTTPException
from app.db import get_conn
from authpad.app.core.security import create_access_token, get_current_user
from authpad.app.utils import verify_pass
from authpad.app.schemas import UserCreate, UserLogin, UserOut


router = APIRouter()


@router.post("/register")
async def register_user(user: UserCreate):
    conn = await get_conn()
    existing = await conn.fetchrow("SELECT * FROM users WHERE email = $1", user.email)
    # check if the email is already registered

    if existing:
        raise HTTPException(status_code=400, detail="it's already registered!")
    await conn.execute(
        "INSERT INTO users (email, hashed_pass) VALUES ($1, $2)", user.email, user.password
    )
    return {"message": "successfully registered!"}


@router.post("/login")
async def login_user(user: UserLogin):
    conn = await get_conn()
    user = conn.fetchrow("SELECT * FROM users WHERE email = $1", user.email)

    if not user or not verify_pass(user.password, user["hashed_pass"]):
        raise HTTPException(status_code=401, detail="Invalid password or email!")
    token = create_access_token({"sub": user.email})
    # 'sub' is the user's unqiue identifier (email)
    return {"access token": token, "token type": "bearer"}


# this will be used for user profile, dashboard, and settings
@router.get("/me", response_model=UserOut)
async def get_me(email: str = Depends(get_current_user)):
    return {"message": email}


# for testing only
@router.get("/protected")
async def protected_area(email: str = Depends(get_current_user)):
    return {"message": f"Hey {email}, you're in a protected area zone!"}