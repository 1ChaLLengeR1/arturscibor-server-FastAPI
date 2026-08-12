from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / "env" / "local.env")

import pytest
from urllib.parse import quote_plus
from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

from config.settings import settings
from database.psql.base import Base

import database.psql.models  # noqa: F401 — registers all models (aboutme, contact, home, projects, tools, users) on Base.metadata

TEST_DB_NAME = f"{settings.db_name}_test"
BASE_URL = f"postgresql://{quote_plus(settings.db_user)}:{quote_plus(settings.db_password)}@{settings.db_host}:{settings.db_port}"
TEST_DB_URL = f"{BASE_URL}/{TEST_DB_NAME}"


def _drop_test_database() -> None:
    """Zrywa WSZYSTKIE sesje na bazie testowej i ją kasuje.

    pg_terminate_backend jest konieczne również przy starcie: jeśli poprzedni przebieg
    został ubity (Ctrl+C / SIGTERM / crash), teardown się nie wykonał i została po nim
    otwarta sesja — samo DROP DATABASE leci wtedy na ObjectInUse ("baza jest używana
    przez innych użytkowników") i wywraca cały run.
    """
    admin_engine = create_engine(f"{BASE_URL}/postgres", isolation_level="AUTOCOMMIT")
    try:
        with admin_engine.connect() as conn:
            conn.execute(text(
                "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                f"WHERE datname = '{TEST_DB_NAME}' AND pid <> pg_backend_pid()"
            ))
            conn.execute(text(f"DROP DATABASE IF EXISTS {TEST_DB_NAME}"))
    finally:
        admin_engine.dispose()


@pytest.fixture(scope="session", autouse=True)
def test_engine():
    _drop_test_database()

    admin_engine = create_engine(f"{BASE_URL}/postgres", isolation_level="AUTOCOMMIT")
    with admin_engine.connect() as conn:
        conn.execute(text(f"CREATE DATABASE {TEST_DB_NAME}"))
    admin_engine.dispose()

    engine = create_engine(TEST_DB_URL)

    with engine.begin() as conn:
        conn.execute(text('CREATE EXTENSION IF NOT EXISTS "pgcrypto"'))

    Base.metadata.create_all(engine)

    try:
        yield engine
    finally:
        # finally, żeby baza znikała także gdy testy padną — DROP DATABASE
        # załatwia sprzątanie schematu, więc drop_all() jest tu zbędne.
        engine.dispose()
        _drop_test_database()


@pytest.fixture(scope="function")
def db_session(test_engine) -> Generator[Session, None, None]:
    TestSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestSession()
    yield session
    session.close()


@pytest.fixture(scope="function", autouse=True)
def clean_tables(test_engine):
    yield
    with test_engine.connect() as conn:
        with conn.begin():
            table_names = ", ".join(t.name for t in reversed(Base.metadata.sorted_tables))
            if table_names:
                conn.execute(text(f"TRUNCATE TABLE {table_names} CASCADE"))