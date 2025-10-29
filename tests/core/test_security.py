import uuid
import pytest
from datetime import timedelta
from app.core.config import settings
from jose import ExpiredSignatureError, JWTError, jwt

from app.core.security import create_access_token



def test_create_access_token_valid():
    data = {"sub": "user@gmail.com"}
    expires = timedelta(minutes=20)

    token = create_access_token(data=data, expires_delta=expires)

    assert isinstance(token, str)

    # Decode token to get data
    decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert decoded["sub"] == "user@gmail.com"
    assert "exp" in decoded

    
    jti = decoded.get("jti")
    assert jti is not None
    assert isinstance(jti, str)  # UUID

    uuid_obj = uuid.UUID(jti)
    assert str(uuid_obj) == jti


def test_token_missing_sub():
    data = {}  # without sub

    with pytest.raises(ValueError):
        create_access_token(data)


def test_token_missing_exp():
    data = {"sub": "user@gmail.com"}
    token = jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)  # without exp
    assert isinstance(token, str)

    decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert "exp" not in decoded


def test_expired_token_should_fail():
    data = {"sub": "expired_user"}
    expires = timedelta(seconds=-1)  # Expired token
    token = create_access_token(data=data, expires_delta=expires)

    with pytest.raises(ExpiredSignatureError):
        jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])


def test_decode_with_wrong_algorithm_and_secret():
    data = {"sub": "user@gmail.com"}
    token = jwt.encode(data, settings.SECRET_KEY, algorithm="HS256")  # Correct algorithm

    with pytest.raises(JWTError):
        jwt.decode(token, settings.SECRET_KEY, algorithms=["RS256"])  # Wrong algorithm

    with pytest.raises(JWTError):
        jwt.decode(token, "wrong-secret", algorithms=[settings.ALGORITHM])


def test_decode_invalid_token():
    broken_token = "asd.fgh.jkl"

    with pytest.raises(JWTError):
        jwt.decode(broken_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])


def test_token_with_large_payload():
    data = {"sub": "user@gmail.com", "meta": "x" * 1000}
    token = create_access_token(data=data)

    decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert decoded["meta"] == "x" * 1000


def test_create_access_token_sets_default_exp():

    token = create_access_token(data={"sub": "test0011"})
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

    assert "exp" in payload


def test_jti_is_unique():
    '''Test that each token gets a unique JWT ID (jti)'''

    first_token = create_access_token(data={"sub": "test0011"})
    second_token = create_access_token(data={"sub": "test0011"})
    
    payload1 = jwt.decode(first_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    payload2 = jwt.decode(second_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

    assert payload1["jti"] != payload2["jti"]


def test_token_with_none_algorithm():
    import base64

    # Simulate attacker creating token with 'none' algorithm
    header = base64.urlsafe_b64encode(b'{"alg":"none","typ":"JWT"}').rstrip(b"=").decode()
    payload = base64.urlsafe_b64encode(b'{"sub":"user123"}').rstrip(b"=").decode()
    token = f"{header}.{payload}."  # No signature - security risk!

    with pytest.raises(jwt.JWTError):
        jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])