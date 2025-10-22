import uuid
import pytest
from datetime import timedelta
from app.core.security import ALGORITHM, SECRET_KEY, create_access_token
from jose import ExpiredSignatureError, JWTError, jwt



def test_create_access_token_valid():
    data = {"sub": "user@gmail.com"}
    expires = timedelta(minutes=20)

    token = create_access_token(data=data, expires_delta=expires)

    assert isinstance(token, str)

    # شکافتن رشته برای استخراج اطلاعات و بررسی مقادیر -> sub & exp
    decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert decoded["sub"] == "user@gmail.com"
    assert "exp" in decoded

    
    jti = decoded.get("jti")
    assert jti is not None
    assert isinstance(jti, str)  # UUID

    uuid_obj = uuid.UUID(jti)
    assert str(uuid_obj) == jti


def test_token_missing_sub():
    data = {}  # بدون sub
    token = create_access_token(data=data)

    assert isinstance(token, str)

    decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert "sub" not in decoded


def test_token_missing_exp():
    data = {"sub": "user@gmail.com"}
    token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)  # بدون exp -> فقط sub (data) داده شده
    assert isinstance(token, str)

    decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert "exp" not in decoded


def test_expired_token_should_fail():
    data = {"Sub": "expired_user"}
    expires = timedelta(seconds=-1)  # منقضی شده
    token = create_access_token(data=data, expires_delta=expires)

    with pytest.raises(ExpiredSignatureError):
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


def test_decode_with_wrong_algorithm_and_secret():
    data = {"sub": "user@gmail.com"}
    token = jwt.encode(data, SECRET_KEY, algorithm="HS256")  # الگوریتم درست

    with pytest.raises(JWTError):
        # الگوریتم اشتباه
        jwt.decode(token, SECRET_KEY, algorithms=["RS256"])

    with pytest.raises(JWTError):
        jwt.decode(token, "wrong-secret", algorithms=[ALGORITHM])


def test_decode_invalid_token():
    broken_token = "asd.fgh.jkl"

    with pytest.raises(JWTError):
        jwt.decode(broken_token, SECRET_KEY, algorithms=[ALGORITHM])


def test_token_with_large_payload():
    data = {"sub": "user@gmail.com", "meta": "x" * 1000}
    token = create_access_token(data=data)

    decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert decoded["meta"] == "x" * 1000
