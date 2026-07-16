from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    api_host: str = "0.0.0.0"
    api_port: int = 8000
    database_url: str = "sqlite:///./data/acronyms.db"
    team_id: str = "default"
    upload_dir: str = "./data/uploads"
    nlp_url: str = "http://127.0.0.1:8001"
    use_mock_nlp: bool = False


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    db_path = settings.database_url.replace("sqlite:///", "")
    if db_path.startswith("./"):
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    return settings
