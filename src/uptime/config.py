from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):

    """Twelve-factor config: everything comes from UPTIME_* environment variables."""
    model_config = SettingsConfigDict(env_prefix="UPTIME_")
    database_url: str = "postgresql+psycopg://uptime:uptime@localhost:5432/uptime"
    check_interval_seconds: int = 30
    check_timeout_seconds: float = 10.0
    # When set, creating/deleting monitors requires "Authorization: Bearer <token>".
    admin_token: str = ""



settings = Settings()
