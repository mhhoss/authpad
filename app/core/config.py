from pydantic import ConfigDict, Field
from pydantic_settings import BaseSettings



class Settings(BaseSettings):
    # Database
    DB_URL: str | None = None

    # JWT Authentication
    SECRET_KEY: str = Field(..., min_length=32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    
    # OTP limits
    OTP_LENGTH: int = 6
    OTP_EXPIRE_MINUTES: int = 10
    OTP_MAX_ATTEMPTS: int = 3

    # Email SMTP
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str
    SMTP_PASSWORD: str
    SMTP_FROM_EMAIL: str = "noreply@authpad.com"

    # Security
    MAX_LOGIN_ATTEMPTS: int = 5
    LOCKOUT_TIME_MINUTES: int = 15
    BCRYPT_ROUNDS: int = 12

    
    model_config = ConfigDict(
    env_file=".env",
    case_sensitive=True
    )



settings = Settings()