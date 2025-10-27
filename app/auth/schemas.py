from pydantic import BaseModel, EmailStr, Field, field_validator


# دریافت اطلاعات ثبت نام
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=72)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: EmailStr) -> EmailStr:
        return v.lower().strip()

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


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int | None = None


# loginrequest
# passwordresetrequest
# OTPVerifyRequest