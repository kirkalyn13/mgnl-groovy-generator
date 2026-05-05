from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader
from pydantic import field_validator
from pydantic_settings import BaseSettings

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=True)

class AuthSettings(BaseSettings):
    api_keys: str = ""

    @field_validator("api_keys", mode="before")
    @classmethod
    def parse_api_keys(cls, v):
        if isinstance(v, str):
            return v
        return ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore" 

    def get_api_keys(self) -> list[str]:
        return [key.strip() for key in self.api_keys.split(",") if key.strip()]

auth_settings = AuthSettings()

def verify_api_key(api_key: str = Security(API_KEY_HEADER)) -> str:
    """Verify if API Key is present from the request header"""
    if api_key not in auth_settings.get_api_keys():
        raise HTTPException(status_code=403, detail="Invalid or missing API key")
    return api_key