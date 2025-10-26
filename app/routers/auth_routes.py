from datetime import timedelta
import asyncpg
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.db.connection import get_conn
from app.core.security import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, get_current_user
from app.services.password import hash_pass, verify_pass
from app.schemas.auth_schemas import TokenResponse, UserOut, UserRegistration


router = APIRouter()


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserRegistration, conn: asyncpg.Connection = Depends(get_conn)):
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

    hashed_password = hash_pass(user.password)

    # ایجاد رکورد و خواندن اطلاعات و سپس برگرداندن آن
    user_row = await conn.fetchrow(
        """
        INSERT INTO users (email, hashed_pass, is_verified) VALUES ($1, $2, $3)
        RETURNING id, email, is_verified, created_at
        """,
        user.email, hashed_password, True
    )

    if not user_row:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User registration failed")

    return UserOut(**user_row)



@router.post("/token", response_model=TokenResponse)
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
    user_row = await conn.fetchrow(
        "SELECT id, email, hashed_pass, is_verified FROM users WHERE email = $1",
        form_data.username
    )

    # اعتبارسنجی رمز عبور
    if not user_row or not verify_pass(form_data.password, user_row["hashed_pass"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # ساخت توکن JWT
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token({"sub": user_row["email"]}, expires_delta=access_token_expires)

    return {"access_token": token, "token_type": "bearer", "expires_in": int(access_token_expires.total_seconds())}


@router.get("/protected")
async def protected_area(user: UserOut = Depends(get_current_user)):
    return UserOut(user)