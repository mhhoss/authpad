from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

MAX_PASSWORD_BYTES = 72
MIN_PASSWORD_CHARS = 8


def hash_password(password: str) -> str:
    if not isinstance(password, str):
        raise ValueError("Password must be a string")
    password = password.strip()
    if not password:
        raise ValueError("Password cannot be empty")
    if len(password.encode("utf-8")) > 72:
        raise ValueError("Password must be at most 72 bytes")

    byte_length = len(password.encode("utf-8"))
    char_length = len(password)

    if byte_length > MAX_PASSWORD_BYTES:
        raise ValueError(f"Password too long for bcrypt (Max: {MAX_PASSWORD_BYTES} bytes)")
    elif char_length < MIN_PASSWORD_CHARS:
        raise ValueError(f"Password too short (Min: {MIN_PASSWORD_CHARS} chars)")
    return pwd_context.hash(password)


def verify_password(plain: str, password_hash: str) -> bool:
    trimmed = plain.encode("utf-8")[:MAX_PASSWORD_BYTES].decode("utf-8", errors="ignore")
    return pwd_context.verify(trimmed, password_hash)
