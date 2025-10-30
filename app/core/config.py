import os


class Settings:
    def __init__(self):
        # Database
        self.DB_URL = os.getenv("DB_URL")

        # JWT Authentication
        self.SECRET_KEY = os.getenv("SECRET_KEY", "test-super-secret-key-1234567890")
        self.ALGORITHM = os.getenv("ALGORITHM", "HS256")
        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))



settings = Settings()