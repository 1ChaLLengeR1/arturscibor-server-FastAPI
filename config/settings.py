from pydantic_settings import BaseSettings, SettingsConfigDict

from config.app import ENV_PATH


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_PATH, env_prefix="ARTURSCIBOR_BACKEND_", extra="ignore")

    db_host: str
    db_port: int = 5432
    db_user: str
    db_password: str
    db_name: str

    secret_admin_token: str
    refresh_admin_token: str
    access_token_expire_hours: int
    refresh_token_expire_hours: int
    algorithm: str

    server: str


settings = Settings()
