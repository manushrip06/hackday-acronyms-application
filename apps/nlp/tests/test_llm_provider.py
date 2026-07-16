from app.config import Settings
from app.define import build_llm_request


def test_build_bedrock_request_uses_openai_compatible_payload() -> None:
    settings = Settings(
        llm_provider="bedrock",
        openai_base_url="",
        bedrock_model_id="gpt-4o-mini",
        bedrock_endpoint="https://example.com/bedrock",
        bedrock_api_key="bedrock-api-key-123",
    )

    provider, url, headers, body = build_llm_request(settings, "system prompt", "user prompt")

    assert provider == "bedrock"
    assert url.endswith("/v1/chat/completions")
    assert headers["Authorization"] == "Bearer bedrock-api-key-123"
    assert headers["Content-Type"] == "application/json"
    assert body["model"] == "gpt-4o-mini"
    assert body["messages"][0]["role"] == "system"


def test_build_request_uses_openai_base_url_when_present() -> None:
    settings = Settings(
        openai_api_key="openai-api-key-123",
        openai_base_url="https://example.com/v1",
        openai_model="gpt-4o-mini",
    )

    provider, url, headers, body = build_llm_request(settings, "system prompt", "user prompt")

    assert provider == "openai"
    assert url.endswith("/chat/completions")
    assert headers["Authorization"] == "Bearer openai-api-key-123"
    assert body["model"] == "gpt-4o-mini"


def test_build_request_uses_token_provider_when_auth_credentials_exist() -> None:
    settings = Settings(
        llm_provider="token",
        auth_token_url="https://auth.example.com/oauth/token",
        auth_client_id="client-id",
        auth_client_secret="client-secret",
        auth_scope="scope1 scope2",
        openai_base_url="https://example.com/v1",
        openai_model="gpt-4o-mini",
    )

    provider, url, headers, body = build_llm_request(settings, "system prompt", "user prompt")

    assert provider == "token"
    assert url.endswith("/chat/completions")
    assert headers["Content-Type"] == "application/json"
    assert body["model"] == "gpt-4o-mini"
