import asyncpg
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.security import verify_token
from app.core.config import settings
from app.db.connection import get_conn


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")



async def get_current_user(
        token: str = Depends(oauth2_scheme),
        conn: asyncpg.Connection = Depends(get_conn)
        ) -> dict:
    '''
    validates the access token and retrieves uer information from the database
    '''

    # standard error for unregistered user
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # get the token from request and decode it to get user email
    try:
        payload = verify_token(token, settings.SECRET_KEY)
        email = payload.get("sub")
        if not email:
            raise credentials_exception
    
    except ValueError:
        raise credentials_exception
    
    query = """
        SELECT id, email, username, password_hash,
        is_verified, is_active, is_superuser,
        created_at, last_login, email_verified_at
        FROM users
        WHERE email = $1
    """

    user_row = await conn.fetchrow(query, email)

    if user_row is None or not user_row["is_verified"] or not user_row["is_active"]:
        raise credentials_exception

    return dict(user_row)
