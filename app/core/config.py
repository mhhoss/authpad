from pydantic import ConfigDict, Field, model_validator
from pydantic_settings import BaseSettings



class Settings(BaseSettings):
    # Database
    DB_URL: str | None = None
    DB_HOST: str | None = None
    DB_PORT: int | None = None
    DB_NAME: str | None = None
    DB_USER: str | None = None
    DB_PASS: str | None = None
    DB_ECHO: str | None = None

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
    FROM_EMAIL: str = "noreply@authpad.com"

    # Security
    MAX_LOGIN_ATTEMPTS: int = 5
    LOCKOUT_TIME_MINUTES: int = 15
    BCRYPT_ROUNDS: int = 12

    
    model_config = ConfigDict(
    env_file=".env",
    case_sensitive=True,
    extra="ignore",
    )


    @model_validator(mode="after")
    def _fill_db_url(self) -> "Settings":
        if self.DB_URL:
            return self

        parts = (self.DB_USER, self.DB_PASS, self.DB_HOST, self.DB_PORT, self.DB_NAME)
        if all(parts):
            self.DB_URL = f"postgresql://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        return self


settings = Settings()