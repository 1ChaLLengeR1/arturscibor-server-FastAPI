from sqlalchemy.orm import Session

from database.psql.models.cv import CurriculumVitae


def create_test_cv(db: Session, *, file_id: str | None = None) -> CurriculumVitae:
    """Testy nie odpalają migracji (`Base.metadata.create_all` w conftest.py,
    nie `alembic upgrade head`), więc seed singletona z migracji nie zadziała —
    trzeba go stworzyć jawnie per test."""
    cv = CurriculumVitae(file_id=file_id)
    db.add(cv)
    db.flush()
    return cv
