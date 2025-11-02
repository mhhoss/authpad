from pydantic import ConfigDict
from pydantic_settings import BaseSettings



class Settings(BaseSettings):
        # Database
        DB_URL: str

        DB_HOST: str
        DB_PORT: int
        DB_NAME: str
        DB_USER: str
        DB_PASS: str

        # JWT Authentication
        SECRET_KEY: str
        ALGORITHM: str = "HS256"
        ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
        
        # OTP limits
        OTP_LENGTH: int = 6
        OTP_EXPIRE_MINUTES: int = 10
        OTP_MAX_ATTEMPTS: int = 3

        # Email SMTP
        SMTP_SERVER: str = "smtp.gmail.com"
        SMTP_PORT: int = 587
        SMTP_USERNAME: str
        SMTP_PASSWORD: str
        FROM_EMAIL: str = "noreply@yourapp.com"

        SMTP_SENDER: str = "test@authpad.com"

        # Security
        MAX_LOGIN_ATTEMPTS: int = 5
        LOCKOUT_TIME_MINUTES: int = 15


        model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True
        )



settings = Settings()