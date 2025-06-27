from pydantic_settings import BaseSettings
import secrets

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "root"
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_DB: str = "farm_automation"
    
    # CORS
    BACKEND_CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:8000"]
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings() 