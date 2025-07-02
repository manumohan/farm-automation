from pydantic_settings import BaseSettings
import secrets
from typing import List, Union
from pydantic import validator
from pydantic import Field

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)  # Should be overridden by env
    ALGORITHM: str = "HS256"  # Should be overridden by env
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # Should be overridden by env
    
    # Database
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "root"
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_DB: str = "farm_automation"
    
    # MQTT
    MQTT_BROKER: str = "localhost"
    MQTT_PORT: int = 1883

    # CORS
    BACKEND_CORS_ORIGINS: Union[str, List[str]] = "http://localhost:3000,http://localhost:8000"

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",") if i.strip()]
        return v
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    offline_threshold_minutes: int = Field(10, description="Minutes after which a device is considered offline")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings() 