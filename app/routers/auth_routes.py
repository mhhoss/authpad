from datetime import timedelta
import uuid
import asyncpg
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.db.db import get_conn
from app.core.security import create_access_token, get_current_user
from app.utils.crypto import hash_pass, verify_pass
from app.schemas.schemas import UserCreate, UserRead, Token


router = APIRouter()


@router.post("/register", response_model=UserRead)
async def register_user(user: UserCreate, conn: asyncpg.Connection = Depends(get_conn)):
    """
    Register a new user with email and password.

    Input:
    - email: must be valid and unique
    - password: plain text, will be hashed

    returns:
    exception error or success message to any client
    """
    existing = await conn.fetchrow("SELECT 1 FROM users WHERE email = $1", user.email)
    # check if the email is already registered

    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The email already registered!")
    
    user_id = str(uuid.uuid4())
    hashed_password = hash_pass(user.password)

    # ایجاد رکورد
    await conn.execute(
        "INSERT INTO users (id, email, hashed_pass, is_verified) VALUES ($1, $2, $3, $4)", user_id, user.email, hashed_password, True
    )

    # خواندن اطلاعات و نهایتا برگرداندن آن به کلاینت
    row = await conn.fetchrow(
        "SELECT id, email, is_verified, created_at FROM users WHERE id = $1",
        user_id
    )

    return UserRead(**row)



@router.post("/token", response_model=Token)
async def token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    conn: asyncpg.Connection = Depends(get_conn)
    ):
    """
    log in an existing user and return a JWT token.

    Input:
    - email: must be registered
    - password: plain text (no hash)

    Returns:
    JWT token or credentials valid
    """

    # گرفتن اطلاعات کاربر از دیتابیس
    row = await conn.fetchrow(
        "SELECT email, hashed_pass FROM users WHERE email = $1",
        form_data.username
    )

    # اعتبارسنجی رمز عبور
    if not row or not verify_pass(form_data.password, row["hashed_pass"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # ساخت توکن JWT
    access_token_expires = timedelta(minutes=60)
    token = create_access_token({"sub": row["email"]}, expires_delta=access_token_expires)

    return Token(access_token=token)


# for testing only
@router.get("/protected")
async def protected_area(email: str = Depends(get_current_user)):
    return UserRead(email=email)