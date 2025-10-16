import asyncpg
from fastapi import APIRouter, Depends, HTTPException
from app.db.db import get_db
from app.core.security import create_access_token, get_current_user
from app.utils.crypto import hash_pass, verify_pass
from app.schemas.schemas import TokenOut, UserCreate, UserLogin, UserOut


router = APIRouter()


@router.post("/register", response_model=UserOut)
async def register_user(user: UserCreate, db: asyncpg.Connection = Depends(get_db)):
    """
    Register a new user with email and password.

    Input:
    - email: must be valid and unique
    - password: plain text, will be hashed

    returns:
    exception error or success message to any client
    """
    existing = await db.fetchrow("SELECT * FROM users WHERE email = $1", user.email)
    # check if the email is already registered

    if existing:
        raise HTTPException(status_code=400, detail="it's already registered!")
    
    hashed = hash_pass(user.password)
    await db.execute(
        "INSERT INTO users (email, hashed_pass) VALUES ($1, $2)", user.email, hashed
    )
    return UserOut(email=user.email)


@router.post("/login", response_model=UserOut)
async def login_user(user: UserLogin, db: asyncpg.Connection = Depends(get_db)):
    """
    log in an existing user and return a JWT token.

    Input:
    - email: must be registered
    - password: plain text (no hash)

    Returns:
    JWT token or credentials valid
    """
    db_user = await db.fetchrow("SELECT * FROM users WHERE email = $1", user.email)

    if not db_user or not verify_pass(user.password, db_user["hashed_pass"]):
        raise HTTPException(status_code=401, detail="Invalid password or email!")

    token = create_access_token({"sub": db_user["email"]})
    # 'sub' is the user's unqiue identifier (email)
    return TokenOut(access_token=token, user=db_user["email"])


# for testing only
@router.get("/protected")
async def protected_area(email: str = Depends(get_current_user)):
    return UserOut(email=email)