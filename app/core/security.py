from jose import jwt
from datetime import timedelta, datetime
import os
from dotenv import load_dotenv


load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"


def create_access_token(data: dict, expires_delta: timedelta=timedelta(minutes=30)):
    # make a jwt token with user info and expiration (default: 30min)
    to_encode = data.copy()
    to_encode["exp"] = datetime.now(datetime.timezone.utc) + expires_delta
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    # Encode the token using the secret key and algorithm