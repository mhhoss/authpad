from datetime import timedelta, datetime, timezone
import asyncpg
from fastapi import APIRouter, Depends, HTTPException, status, Body

from app.db.connection import get_conn
from app.core.security import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token
from app.auth.services.password import hash_password, verify_password
from app.auth.services.jwt import create_refresh_token, verify_refresh_token
from app.auth.schemas import (
    EmailVerificationRequestResponse,
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    VerifyEmailRequest,
    VerifyTokenResponse,
)
from app.user.schemas import UserOut
from app.auth.dependencies import get_current_user
from app.auth.services.otp import EmailService, OTPService
from app.core.config import settings


router = APIRouter()
otp_service = OTPService()


def _normalize_email(email: str) -> str:
    email = (email or "").strip().lower()
    if "@" not in email or email.startswith("@") or email.endswith("@") or "." not in email.split("@")[-1]:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid email format")
    return email


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register_user(
    user: RegisterRequest,
    conn: asyncpg.Connection = Depends(get_conn)
    ) -> UserOut:
    '''
    Register a new user with email and password.

    Parameters:

        - user (RegisterRequest): must be valid and unique.
        - conn (asyncpg.Connection): database connection dependency.

    Responses:

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
    payload: LoginRequest,
    conn: asyncpg.Connection = Depends(get_conn)
    ) -> TokenResponse:
    '''
    Authenticates an existing user and returns a JWT token pair.

    Parameters:
        - payload (LoginRequest): Contains user's email (username) and password.
            Email must be registered. Password is plain text and will be verified.
        - Conn (asyncpg.Connection): Database connection dependency.

    Responses:
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
        _normalize_email(payload.username)
    )

    now = datetime.now(timezone.utc)

    # Lockout check (only if the user exists)
    if user_row and user_row["locked_until"] and user_row["locked_until"] > now:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account temporarily locked due to too many failed login attempts",
        )

    # Validate credentials
    if (not user_row) or (not verify_password(payload.password, user_row["password_hash"])):
        # If the user exists, track failed attempts and potentially lock the account.
        if user_row:
            attempts = int(user_row["failed_login_attempts"] or 0) + 1
            locked_until = None
            if attempts >= settings.MAX_LOGIN_ATTEMPTS:
                locked_until = now + timedelta(minutes=settings.LOCKOUT_TIME_MINUTES)

            await conn.execute(
                """
                UPDATE users
                SET failed_login_attempts = $1, locked_until = $2
                WHERE id = $3
                """,
                attempts,
                locked_until,
                user_row["id"],
            )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
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

    # Successful login: reset lockout counters and update last_login
    await conn.execute(
        """
        UPDATE users
        SET failed_login_attempts = 0, locked_until = NULL, last_login = $1
        WHERE id = $2
        """,
        now,
        user_row["id"],
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
    
    Parameters:
        - refresh_token (str): The refresh token previously issued from the /token endpoint.
        - conn (asyncpg.Connection): Database connection dependency.

    Responses:
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



@router.post("/request-verification", response_model=EmailVerificationRequestResponse)
@router.post("/request-email-verification", response_model=EmailVerificationRequestResponse)
async def verificate_email_request(
    email: str = Body(..., embed=True),
    conn: asyncpg.Connection = Depends(get_conn)
    ) -> dict:
    '''
    Sends a one-time password (OTP) to the user's email for verification.

    Parameters:
        - email (EmailStr): The user's email address. Must be valid and not already verified.
        - conn (asyncpg.Connection): Database connection dependency.

    Responses:
        - EmailVerificationRequestResponse: Contains a success message and metadata (e.g. expires_in) about the OTP request.

    Raises:
        HTTPException:
            - 400 - If the email format is invalid or already verified.
            - 500 - If sending the email fails due to server or provider issues.
    '''

    email = _normalize_email(email)

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
    
    # Invalidate previous OTPs for this user and type
    await conn.execute(
        """
        UPDATE otp_tokens
        SET used_at = $1
        WHERE user_id = $2 AND otp_type = $3 AND used_at IS NULL
        """,
        datetime.now(timezone.utc),
        user_row["id"],
        "email_verification",
    )

    # Generate new OTP
    otp = OTPService.generate_otp()
    token_hash = OTPService.hash_token(otp)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)

    await conn.execute(
        """
        INSERT INTO otp_tokens
        (user_id, otp_type, token_hash, destination, expires_at, attempts)
        VALUES ($1, $2, $3, $4, $5, $6)
        """,
        user_row["id"], "email_verification", token_hash, email, expires_at, 0
    )
    
    # Send email
    email_service = EmailService()
    await email_service.send_verification_email(email, otp)


    return EmailVerificationRequestResponse(
        message="Verification code send to your email",
        expires_in=settings.OTP_EXPIRE_MINUTES
    )



@router.post("/verify-email", response_model=VerifyTokenResponse)
async def verify_email(
    payload: VerifyEmailRequest,
    conn: asyncpg.Connection = Depends(get_conn),
) -> VerifyTokenResponse:
    '''
    Verify a user's email using the OTP previously generated through /request-email-verification.

    this endpoint fetches the stored OTP hash from the database (never from the client),
    validates the OTP format/length, enforces expiry/max-attempts, and marks the user verified.
    '''

    user_row = await conn.fetchrow(
        "SELECT id, is_verified FROM users WHERE email = $1",
        payload.email,
    )
    if not user_row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if user_row["is_verified"]:
        return VerifyTokenResponse(success=True, message="Email already verified")

    now = datetime.now(timezone.utc)
    token_row = await conn.fetchrow(
        """
        SELECT id, token_hash, expires_at, attempts, used_at
        FROM otp_tokens
        WHERE user_id = $1
          AND otp_type = $2
          AND destination = $3
          AND used_at IS NULL
        ORDER BY created_at DESC
        LIMIT 1
        """,
        user_row["id"],
        "email_verification",
        payload.email,
    )

    if not token_row:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active verification token found",
        )

    if token_row["expires_at"] <= now:
        # Mark as used so it can't be replayed.
        await conn.execute(
            "UPDATE otp_tokens SET used_at = $1 WHERE id = $2",
            now,
            token_row["id"],
        )
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Verification token expired")

    attempts = int(token_row["attempts"] or 0)
    if attempts >= settings.OTP_MAX_ATTEMPTS:
        await conn.execute(
            "UPDATE otp_tokens SET used_at = $1 WHERE id = $2",
            now,
            token_row["id"],
        )
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Too many attempts")

    try:
        is_valid = otp_service.verify_input_token(
            payload.otp,
            token_row["token_hash"],
            expected_length=settings.OTP_LENGTH,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    if not is_valid:
        await conn.execute(
            "UPDATE otp_tokens SET attempts = attempts + 1 WHERE id = $1",
            token_row["id"],
        )
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    # Mark token used and user verified
    await conn.execute(
        "UPDATE otp_tokens SET used_at = $1 WHERE id = $2",
        now,
        token_row["id"],
    )
    await conn.execute(
        """
        UPDATE users
        SET is_verified = true, email_verified_at = $1
        WHERE id = $2
        """,
        now,
        user_row["id"],
    )
    return VerifyTokenResponse(success=True, message="Email verified successfully")


@router.post("/logout")
async def logout_user(

    current_user: dict = Depends(get_current_user),
    ) -> dict:
    '''
    Logout authenticated user.

    Parameters:
        - current_user (dict): The authenticated user extracted from the JWT access token.
    
    Responses:
        - dict: A confirmation message with a logout timestamp.
    '''

    return {
        "message": f"User {current_user['email']}, logged out successfully",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }