from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

from config.app import BASE_DIR, ENV_PATH


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

    # Produkcyjny origin frontendu (docs/README.md) — jedyny nie-localhost origin
    # dopuszczony przez CORS w main.py. Nadpisywalny przez env, gdyby domena się zmieniła.
    frontend_url: str = "https://arturscibor.pl"

    # Absolutna ścieżka do katalogu z uploadami — nigdy względna do CWD procesu,
    # bo gunicorn/testy startują z różnych katalogów i zapis trafiałby wtedy
    # w inne miejsce niż mount StaticFiles w main.py.
    static_root: Path = BASE_DIR / "static" / "files"


settings = Settings()
