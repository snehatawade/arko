from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database - defaults to SQLite for easy setup, can override with PostgreSQL
    DATABASE_URL: str = "sqlite:///./billwise.db"
    
    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production-min-32-characters-long-for-security"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Twilio
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_WHATSAPP_FROM: str = "whatsapp:+14155238886"
    
    class Config:
        env_file = ".env"

settings = Settings()

