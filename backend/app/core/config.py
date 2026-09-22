from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "PulseTrade API"
    environment: str = "development"
    database_url: str
    secret_key: str
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30

    deriv_client_id: str
    deriv_redirect_uri: str
    deriv_auth_url: str = "https://auth.deriv.com/oauth2/auth"
    deriv_token_url: str = "https://auth.deriv.com/oauth2/token"
    deriv_api_base: str = "https://api.derivws.com"
    token_encryption_key: str
    redis_url: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()