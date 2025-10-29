from datetime import timedelta
from datetime import datetime, timezone
import asyncpg
from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm

from app.db.connection import get_conn
from app.core.security import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token
from app.auth.services.password import hash_pass, verify_pass
from app.auth.services.jwt import create_refresh_token, verify_refresh_token
from app.auth.schemas import RegisterRequest, TokenResponse
from app.user.schemas import UserOut
from app.auth.dependencies import get_current_user, oauth2_scheme


router = APIRouter()


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register_user(
    user: RegisterRequest,
    conn: asyncpg.Connection = Depends(get_conn)
    ) -> UserOut:
    '''
    Register a new user with email and password.

    Input:
    - email: must be valid and unique
    - password: plain text, will be hashed

    Returns:
    - User data without *sensitive information (id, email, is_verified, created_at)

    Raises:
    - 400: If email already registered
    - 500: If registration fails
    '''

    # Check if the email is already registered
    existing = await conn.fetchrow("SELECT 1 FROM users WHERE email = $1", user.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered!"
            )

    hashed_password = hash_pass(user.password)

    user_row = await conn.fetchrow(
        """
        INSERT INTO users (email, hashed_pass, is_verified) VALUES ($1, $2, $3)
        RETURNING id, email, is_verified, created_at
        """,
        user.email, hashed_password, True
    )

    if not user_row:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User registration failed"
            )

    return UserOut(**user_row)



@router.post("/token", response_model=TokenResponse)
async def token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    conn: asyncpg.Connection = Depends(get_conn)
    ) -> TokenResponse:
    '''
    Log in an existing user and return a JWT token.

    Input:
    - Email: Must be registered
    - Password: Plain text password

    Returns:
    - access_token: JWT token for API authentication
    - refresh_token: Token for obtaining new access tokens
    - token_type: Always "bearer"
    - expires_in: Access token expiration in seconds

    Raises:
    - 401: If email or password is incorrect
    - 403: If user email is not verified
    '''

    # Get user from database
    user_row = await conn.fetchrow(
        "SELECT id, email, hashed_pass, is_verified FROM users WHERE email = $1",
        form_data.username
    )

    # Validate credentials
    if not user_row or not verify_pass(form_data.password, user_row["hashed_pass"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Check if user is verified
    if not user_row["is_verified"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email address before logging in"
        )

    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        {"sub": user_row["email"]},
        expires_delta=access_token_expires
        )
    
    # Create refresh token
    refresh_token = create_refresh_token({"sub": user_row["email"]})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=int(access_token_expires.total_seconds())
    )



@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_token: str = Body(..., embed=True),
    conn: asyncpg.Connection = Depends(get_conn)
) -> TokenResponse:
    '''
    Refresh expired access token using valid refresh token.
    
    Input:
    - refresh_token: Valid refresh token received from /token endpoint

    Returns:
    - New access token and optional new refresh token
    - token_type: Always "bearer"
    - expires_in: Token expiration in seconds

    Raises:
    - 401: If refresh token is invalid or expired
    - 404: If user not found
    - 403: If user email not verified
    '''

    try:
        # Verify refresh token
        payload = verify_refresh_token(refresh_token)
        user_email = payload.get("sub")
        
        # Check if user exists
        user_row = await conn.fetchrow(
            """
            SELECT email, is_verified 
            FROM users 
            WHERE email = $1
            """,
            user_email
        )
        
        if not user_row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
            
        # Check if user is verified
        if not user_row["is_verified"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please verify your email first"
            )
        
        # Create new access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        new_access_token = create_access_token(
            {"sub": user_email}, 
            expires_delta=access_token_expires
        )
        
        # Create new refresh token
        new_refresh_token = create_refresh_token({"sub": user_email})
        
        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=int(access_token_expires.total_seconds())
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid refresh token: {str(e)}"
            )
    


@router.post("/logout")
async def logout_user(
    current_user: str = Depends(get_current_user),
    token: str = Depends(oauth2_scheme)
    ) -> dict:
    '''
    Logout user and revoke current access token.

    Input:
    - Requires valid access token in Authorization header

    Returns:
    dict: Success message with revocation information
    '''

    return {
        "message": "Successfully logged out",
        "revoked": True,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }