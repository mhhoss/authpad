from datetime import timedelta, datetime, timezone
import asyncpg
from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr

from app.db.connection import get_conn
from app.core.security import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token
from app.auth.services.password import hash_password, verify_password
from app.auth.services.jwt import create_refresh_token, verify_refresh_token
from app.auth.schemas import EmailVerificationRequestResponse, RegisterRequest, TokenResponse, VerifyTokenResponse
from app.user.schemas import UserOut
from app.auth.dependencies import get_current_user
from app.auth.services.otp import EmailService, OTPService
from app.core.config import settings


router = APIRouter()
otp_service = OTPService()



@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register_user(
    user: RegisterRequest,
    conn: asyncpg.Connection = Depends(get_conn)
    ) -> UserOut:
    '''
    Register a new user with email and password.

    Args:
        - user (RegisterRequest): must be valid and unique.
        - conn (asyncpg.Connection): database connection dependency.

    Returns:
        - UserOut: The newly created user object.

    Raises:
        HTTPExeption:
            - 400: If email already registered.
            - 500: If registration fails.
    '''

    # Check if the email is already registered
    existing = await conn.fetchrow("SELECT 1 FROM users WHERE email = $1", user.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered!"
            )

    password_hash = hash_password(user.password)

    user_row = await conn.fetchrow(
        """
        INSERT INTO users (email, password_hash)
        VALUES ($1, $2)
        RETURNING id, email, is_verified, is_active, created_at
        """,
        user.email, password_hash
    )

    if not user_row:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User Registeration failed"
        )

    return UserOut(**user_row)



@router.post("/token", response_model=TokenResponse)
async def token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    conn: asyncpg.Connection = Depends(get_conn)
    ) -> TokenResponse:
    '''
    Authenticates an existing user and returns a JWT token pair.

    Args:
        - form_data (OAuth2PasswordRequestForm): Contains user's email and password.
            Email must be registered. Password is plain text and will be verified.
        - Conn (asyncpg.Connection): Database connection dependency.

    Returns:
        - TokenResponse: Includes access token, refresh token, token type ("bearer"), and expiration time in seconds.

    Raises:
        HTTPExeption:
            - 401: If email or password is incorrect.
            - 403: If user email is not verified.
    '''

    # Get user from database
    user_row = await conn.fetchrow(
        """
        SELECT id, email, password_hash, is_verified, is_active,
        failed_login_attempts, locked_until
        FROM users WHERE email = $1
        """,
        form_data.username
    )

    # Validate credentials
    if not user_row or not verify_password(form_data.password, user_row["password_hash"]):
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
    
    # Check if user is active
    if not user_row["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
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
    Refreshes an expired access token using valid refresh token.
    
    Args:
        - refresh_token (str): The refresh token previously issued from the /token endpoint.
        - conn (asyncpg.Connection): Database connection dependency.

    Returns:
        - TokenResponse: Contains a new access token, optional new refresh token, token type ("bearer"),
            and expiration time in seconds.
        
    Raises:
        HTTPExeption:
            - 401: If refresh token is invalid or expired.
            - 404: If user not found.
            - 403: If the user's email is not verified.
    '''

    try:
        # Verify refresh token
        payload = verify_refresh_token(refresh_token)
        user_email = payload.get("sub")
        
        # Check if user exists
        user_row = await conn.fetchrow(
            """
            SELECT email, is_verified, is_active
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
        
        # Check if user is active
        if not user_row["is_active"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated"
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



@router.post("/request-email-verification", response_model=EmailVerificationRequestResponse)
async def verificate_email_request(
    email: EmailStr = Body(..., embed=True),
    conn: asyncpg.Connection = Depends(get_conn)
    ) -> dict:
    '''
    Sends a one-time password (OTP) to the user's email for verification.

    Args:
        - email (EmailStr): The user's email address. Must be valid and not already verified.
        - conn (asyncpg.Connection): Database connection dependency.

    Returns:
        - EmailVerificationRequestResponse: Contains a success message and metadata (e.g. expires_in) about the OTP request.

    Raises:
        HTTPException:
            - 400 - If the email format is invalid or already verified.
            - 500 - If sending the email fails due to server or provider issues.
    '''

    user_row = await conn.fetchrow(
        """
        SELECT id, email, is_verified
        FROM users
        WHERE email = $1
        """,
        email
    )
    
    if not user_row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if already registered
    if user_row["is_verified"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified!"
        )
    
    '''Invalidate previous OTPs for this user and type'''
    await conn.execute(
        """
        UPDATE otp_tokens
        SET is_used = true 
        WHERE user_id = $1 AND token_type = $2
        """,
        user_row["id"], "email_verification"
    )

    # Generate new OTP
    otp = OTPService.generate_otp()
    token_hash = OTPService.hash_token(otp)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

    await conn.execute(
        """
        INSERT INTO otp_tokens
        (user_id, otp_type, token_hash, destination, expires_at)
        VALUES ($1, $2, $3, $4, $5)
        """,
        user_row["id"], "email_verification", token_hash, email, expires_at
    )
    
    # Send email
    email_service = EmailService()
    await email_service.send_verification_email(email, otp)


    return EmailVerificationRequestResponse(
        message="Verification code send to your email",
        expires_in=settings.OTP_EXPIRE_MINUTES
    )



@router.post("verify-token", response_model=VerifyTokenResponse)
async def token_verify(
    input_token: str,
    stored_hash: str,
    otp_length: int = Depends(lambda: settings.OTP_LENGTH)
    ) -> VerifyTokenResponse:
    '''
    Verifies a one-time password (OTP) entered by the user.

    Args:
        - input_token (str): The OTP entered by the user.
        - stored_hash (str): The hashed version of the original OTP stored in the database or cache.
        - otp_length (int): Expected length of the OTP (default from settings).

    Returns:
        - VerifyTokenResponse: Contains a success flag and a message indicating the result of the verification.

    Raises:
        HTTPException:
            - 401: If the token format is invalid or does not match the stored hash.
    '''

    if not otp_service.verify_input_token(
        input_token,
        stored_hash,
        expected_length=Depends(otp_length)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format or mismatch"
        )
    
    return VerifyTokenResponse(
        success=True,
        message="Token verified successfully"
    )



@router.post("/logout")
async def logout_user(

    current_user: dict = Depends(get_current_user),
    ) -> dict:
    '''
    Logout authenticated user.

    Args:
        - current_user (dict): The authenticated user extracted from the JWT access token.
    
    Returns:
        - dict: A confirmation message with a logout timestamp.
    '''

    return {
        "message": f"User {current_user['email']}, logged out successfully",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }