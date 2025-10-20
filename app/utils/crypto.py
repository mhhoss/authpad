from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

MAX_PASSWORD_BYTES = 72
MIN_PASSWORD_CHARS = 8


def hash_pass(password: str) -> str:
    password = password.strip()
    byte_length = len(password.encode("utf-8"))
    char_length = len(password)

    if byte_length > MAX_PASSWORD_BYTES:
        raise ValueError(f"Password too long for bcrypt (Max: {MAX_PASSWORD_BYTES} bytes)")
    elif char_length < MIN_PASSWORD_CHARS:
        raise ValueError(f"Password too short (Min: {MIN_PASSWORD_CHARS} chars)")
    return pwd_context.hash(password)


def verify_pass(plain: str, hashed_password: str) -> bool:
    trimmed = plain.encode("utf-8")[:MAX_PASSWORD_BYTES].decode("utf-8", errors="ignore")
    return pwd_context.verify(trimmed, hashed_password)
