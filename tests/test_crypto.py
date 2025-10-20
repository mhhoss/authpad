import pytest
from app.utils.crypto import hash_pass, verify_pass


def test_hash_and_verify():
    password= "123kfoel"
    wrong_pass = "h8Njdj3k"

    hashed = hash_pass(password)
    assert verify_pass(password, hashed)
    assert not verify_pass(wrong_pass, hashed)


def test_hash_is_different_each_time():
    password = "123kfoel"
    
    hashed1 = hash_pass(password)
    hashed2 = hash_pass(password)
    assert hashed1 != hashed2


def test_password_rejections():
    short_pass = "abc"
    long_pass = "a" * 100

    with pytest.raises(ValueError):
        hash_pass(short_pass)

    with pytest.raises(ValueError):
        hash_pass(long_pass)


def test_verify_trims():  # to 72 bytes
    password = "a" * 100
    trimmed = password.encode("utf-8")[:72].decode("utf-8", errors="ignore")
    hashed = hash_pass(trimmed)

    assert verify_pass(trimmed, hashed)


def test_special_chars_password():
    password = "!@#$_-+=[]{}|:;<>?/\\\"'`~^&*()"
    hashed = hash_pass(password)
    assert verify_pass(password, hashed)

    wrong_password = "!@#$_-+=[]{}|:;<>?/\\\"'`~^&*("  # one char removed
    assert not verify_pass(wrong_password, hashed)
