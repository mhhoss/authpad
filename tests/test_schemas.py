from pydantic import ValidationError
import pytest
from app.schemas.schemas import UserCreate


def test_short_password_rejected():  # less than 8 chars
    with pytest.raises(ValidationError):
        UserCreate(email= "mahdi@gmail.com", password= "021")


def test_long_password_rejected():  # more than 72 chars
    long_pass = "abc" * 30
    with pytest.raises(ValidationError):
        UserCreate(email= "mahdi@gmail.com", password=long_pass)


def test_password_with_spaces():
    password= "  123abcde  "
    user= UserCreate(email= "mahdi@gmail.com", password=password)
    assert user.password == password.strip()


def test_invalid_email_rejected():
    with pytest.raises(ValidationError):
        UserCreate(email= "justtext", password= "validpass0101")