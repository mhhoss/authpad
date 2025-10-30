import uuid
from jose import JWTError, jwt
from datetime import timedelta, datetime, timezone
from app.core.config import settings
import os
from dotenv import load_dotenv



load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY not set in (.env) file")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))



def create_access_token(
        data: dict,
        secret_key: str = settings.SECRET_KEY,
        algorithm: str = settings.ALGORITHM,
        expires_delta: timedelta | None = None
        ) -> str:
    '''create JWT access token'''
    
    if "sub" not in data:
        raise ValueError("Token data must contain 'sub' claim")

    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )

    to_encode.update({
        "exp": expire,
        "jti": str(uuid.uuid4()),
        "iat": datetime.now(timezone.utc)
        })
    
    token = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return token



def verify_token(
        token: str,
        secret_key: str = settings.SECRET_KEY,
        algorithm: str = settings.ALGORITHM
        ) -> dict:
    '''verify and decode JWT token'''

    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        return payload
    except JWTError as e:
        raise ValueError(f"Invalid or expired token: {str(e)}")

