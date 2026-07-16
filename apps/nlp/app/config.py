from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    openai_base_url: str = ""
    llm_provider: str = "openai"
    auth_token_url: str = ""
    auth_client_id: str = ""
    auth_client_secret: str = ""
    auth_scope: str = ""
    auth_grant_type: str = "client_credentials"
    azure_openai_api_key: str = ""
    azure_openai_endpoint: str = ""
    azure_openai_deployment: str = ""
    bedrock_model_id: str = "anthropic.claude-3-5-sonnet-20240620-v1:0"
    bedrock_region: str = "us-east-1"
    bedrock_endpoint: str = ""
    bedrock_api_key: str = ""
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_session_token: str = ""
    noun_phrase_min_freq: int = 2


@lru_cache
def get_settings() -> Settings:
    return Settings()
