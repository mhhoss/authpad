import os


class Settings:
    def __init__(self):
        # Database
        self.DB_URL = os.getenv("DB_URL")

        # JWT Authentication
        self.SECRET_KEY = os.getenv("SECRET_KEY")
        self.ALGORITHM = os.getenv("ALGORITHM", "HS256")
        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

        if not self.DB_URL:
            raise RuntimeError("DB_URL environment variable is required")
        
        if not self.SECRET_KEY:
            raise RuntimeError("SECRET_KEY environment variable is required")




settings = Settings()