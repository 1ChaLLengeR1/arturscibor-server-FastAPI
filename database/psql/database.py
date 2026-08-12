from collections.abc import Generator, Iterator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from config.settings import settings

DATABASE_URL = (
    f"postgresql+psycopg2://{settings.db_user}:{settings.db_password}"
    f"@{settings.db_host}:{settings.db_port}/{settings.db_name}"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency — one session per request, commit on success."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


@contextmanager
def managed_session(db_session: Session | None = None) -> Iterator[tuple[Session, bool]]:
    """Reuse a session passed in from an endpoint (get_db already owns the
    commit), or open and commit a standalone one when called outside a
    request (tests, scripts)."""
    if db_session is not None:
        yield db_session, False
        return

    session = SessionLocal()
    try:
        yield session, True
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
