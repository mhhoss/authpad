from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from app.core.config import settings


def create_refresh_token(
    data: dict,
    expire_delta: timedelta = None
    ) -> str:
    '''Create refresh token with longer expiration (30 days default)'''

    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expire_delta or timedelta(days=30)

    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "refresh"
    })

    token = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
        )
    return token

    
def verify_refresh_token(token: str) -> dict:
    '''Verify refresh token signature and expiration'''
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        # Check if it's a refresh token
        if payload.get("type") != "refresh":
            raise ValueError("Not a refresh token")
        
        return payload
    
    except JWTError as e:
        raise ValueError(
            f"Invalid refresh token {str(e)}"
        )