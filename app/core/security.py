from email.policy import HTTP
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import timedelta, datetime
import os
from dotenv import load_dotenv


load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def create_access_token(data: dict, expires_delta: timedelta=timedelta(minutes=30)):
    # make a jwt token with user info and expiration (default: 30min)
    to_encode = data.copy()
    to_encode["exp"] = datetime.now(datetime.timezone.utc) + expires_delta
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    # Encode the token using the secret key and algorithm


async def get_current_user(token: str = Depends(oauth2_scheme)):
    # get the token from request
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            return HTTPException(status_code=401, detail="Invalid token!")
        return email
    
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token!")
