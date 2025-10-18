import uuid
import asyncpg
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import timedelta, datetime, timezone
import os
from dotenv import load_dotenv

from app.db.db import get_conn


load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY not set in (.env) file")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")



def create_access_token(data: dict, expires_delta: timedelta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)) -> str:
    # make a jwt token with user info and expiration (default: 30min)
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta)
    to_encode.update({"exp": expire, "jti": str(uuid.uuid4())})  # برای ردیابی توکن ها
    
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token



async def get_current_user(
        token: str = Depends(oauth2_scheme), conn: asyncpg.Connection = Depends(get_conn)
        ) -> asyncpg.Record:  # خروجی fetchrow

    # یک ارور استاندارد برای زمانی که کلاینت نیاز به احراز هویت داره
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    conn: asyncpg.Connection = Depends(get_conn)

    # get the token from request and decode it to get user email
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
    
    except JWTError:
        raise credentials_exception

    query = """
        SELECT id, email, username, hashed_pass, is_verified, created_at, last_login
        FROM users
        WHERE email = $1
    """
    row = await conn.fetchrow(query, email)

    if row is None or not row.get("is_verified", False):
        raise credentials_exception

    return row

