from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "PocketSmart AI"
    secret_key: str = "change-me"
    database_url: str = "sqlite:///./pocketsmart.db"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.8-flash"
    access_token_expire_minutes: int = 120
    max_upload_mb: int = 5
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")

settings = Settings()
