from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Order Service API"
    DATABASE_URL: str = "sqlite:///./orders.db"
    
settings = Settings()
