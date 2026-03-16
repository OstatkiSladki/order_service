from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Order Service API"
    VERSION: str = "1.2.0"
    API_V1_STR: str = "/api/v1"
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

settings = Settings()
