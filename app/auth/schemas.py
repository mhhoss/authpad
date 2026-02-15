from pydantic import BaseModel, Field, field_validator


# User registration input validation
class RegisterRequest(BaseModel):
    email: str
    password: str = Field(..., min_length=8, max_length=72)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        v = v.lower().strip()
        if "@" not in v or v.startswith("@") or v.endswith("@") or "." not in v.split("@")[-1]:
            raise ValueError("Invalid email format")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 8 or len(v) > 72:
            raise ValueError("Password must be between 8 and 72 chars long")
        return v
    
    model_config = {
        "extra": "forbid"
    }


# Authentication token response
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"
    expires_in: int | None = None


class LoginRequest(BaseModel):
    username: str
    password: str

    model_config = {"extra": "forbid"}


class EmailVerificationRequestResponse(BaseModel):
    message: str
    expires_in: int


class VerifyTokenResponse(BaseModel):
    success: bool
    message: str


class VerifyEmailRequest(BaseModel):
    email: str
    otp: str = Field(..., min_length=1, max_length=32)