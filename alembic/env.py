"""Alembic environment.

- Loads the same env vars the app uses to build the DB URL (single source).
- Imports `database.psql.models` so every model registers on Base.metadata
  before autogenerate runs — otherwise alembic would think the schema is
  empty and propose dropping every table.
"""

from logging.config import fileConfig

from sqlalchemy import URL, engine_from_config, pool

# Importing the models package triggers all model imports, populating
# Base.metadata. Required for autogenerate to work.
import database.psql.models  # noqa: F401
from alembic import context
from config.settings import settings
from database.psql.base import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _build_database_url() -> URL:
    return URL.create(
        drivername="postgresql+psycopg2",
        username=settings.db_user,
        password=settings.db_password,
        host=settings.db_host,
        port=settings.db_port,
        database=settings.db_name,
    )


def run_migrations_offline() -> None:
    """Emit SQL to stdout without connecting to a database."""
    context.configure(
        url=_build_database_url().render_as_string(hide_password=False),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = _build_database_url().render_as_string(hide_password=False)

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
