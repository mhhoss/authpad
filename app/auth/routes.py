from fastapi import APIRouter, HTTPException
from app.db import get_conn


router = APIRouter()


@router.post("/register")
async def register_user(email: str, password: str):
    conn = await get_conn()
    existing = await conn.fetchrow("SELECT * FROM users WHERE email = $1", email)
    # check if the email is already registered
    if existing:
        raise HTTPException(status_code=400, detail="it's already registered!")
    await conn.execute(
        "INSERT INTO users (email, hashed_pass) VALUES ($1, $2)", email, password
    )
    return {"message": "successfully registered!"}




'''هش کردن رمز در /register
نوشتن /login با JWT
ساخت middleware برای محافظت از routeها
تأیید ایمیل
بازیابی رمز'''

