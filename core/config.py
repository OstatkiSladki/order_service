from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
  model_config = SettingsConfigDict(env_file=".env", extra="ignore")

  app_name: str = "order-service"
  app_env: str = "production"
  app_host: str = "0.0.0.0"
  app_port: int = 8004
  app_root_path: str = ""
  app_debug: bool = False
  log_level: str = "INFO"

  db_host: str = "localhost"
  db_port: int = 5432
  db_name: str = "db_order"
  db_user: str = "postgres"
  db_password: str = "postgres"
  db_pool_size: int = 10
  db_max_overflow: int = 20

  @property
  def database_dsn(self) -> str:
    return (
      f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
      f"@{self.db_host}:{self.db_port}/{self.db_name}"
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
  return Settings()
