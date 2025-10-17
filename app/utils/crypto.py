from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_pass(password: str) -> str:
    trimmed = password.encode("utf-8")[:72].decode("utf-8", errors="ignore")
    return pwd_context.hash(trimmed)

def verify_pass(plain: str, hashed: str) -> bool:
    trimmed = plain.encode("utf-8")[:72].decode("utf-8", errors="ignore")
    return pwd_context.verify(trimmed, hashed)
