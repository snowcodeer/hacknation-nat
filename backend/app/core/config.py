from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # OpenAI
    openai_api_key: str
    openai_model: str = "gpt-4.1"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True

    # CORS
    allowed_origins: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # File Upload
    upload_dir: str = "uploads"
    max_upload_size: int = 10485760  # 10MB

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
