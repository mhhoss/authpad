from datetime import datetime, timezone
from uuid import uuid4
from pydantic import ValidationError
import pytest
from app.auth.schemas import RegisterRequest, TokenResponse
from app.user.schemas import UserOut


def test_user_create_schema_valid():
    data = {
        "email": "user@email.com",
        "password": "nJgTf66Frnkl"
    }
    schema = RegisterRequest(**data)

    assert schema.email == "user@email.com"
    assert schema.password == "nJgTf66Frnkl"
    assert isinstance(schema, RegisterRequest)


def test_short_password_rejected():  # less than 8 chars
    with pytest.raises(ValidationError):
        RegisterRequest(email= "mahdi@gmail.com", password= "021")


def test_long_password_rejected():  # more than 72 chars
    long_pass = "abc" * 30
    with pytest.raises(ValidationError):
        RegisterRequest(email= "mahdi@gmail.com", password=long_pass)


def test_password_with_spaces():
    password= "  123abcde  "
    user= RegisterRequest(email= "mahdi@gmail.com", password=password)
    assert user.password == password.strip()


def test_invalid_email_rejected():
    with pytest.raises(ValidationError):
        RegisterRequest(email= "justtext", password= "validpass0101")


def test_email_normalization():
    email = "  MaHdi@gmail.com  "

    assert email.strip().lower() == "mahdi@gmail.com"


def test_extra_input():
    with pytest.raises(ValidationError):
        RegisterRequest(
        email="asfghkd@gmail.com",
        password="HimT3gJn%k",
        is_active=True  # extra field
    )
        

def test_created_at_defaults_to_none():
    user = UserOut(
        id=uuid4(),
        email="test@example.com",
        is_verified=False
    )

    assert user.created_at is None


def test_expires_in_defaults_to_none():
    user = TokenResponse(
        access_token="nJGmk850n",
        token_type="bearer"
    )

    assert user.expires_in is None


def test_userout_output_has_only_allowed_fields():
    user = UserOut(
        id=uuid4(),
        email="test@gmail.com",
        is_verified=True,
        created_at=datetime.now(timezone.utc)
    )

    output = user.model_dump()
    assert set(output.keys()) == {"id", "email", "is_verified", "created_at"}


def test_token_output_has_only_allowed_fields():
    user = TokenResponse(
        access_token="jBgi8JhImG&np",
        token_type="bearer",
        refresh_token="refresh_token",
        expires_in=3600
    )

    output = user.model_dump()
    assert set(output.keys()) == {"access_token", "token_type","refresh_token" , "expires_in"}