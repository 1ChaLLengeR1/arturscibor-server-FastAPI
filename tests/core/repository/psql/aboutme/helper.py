from sqlalchemy.orm import Session

from database.psql.models.aboutme import AboutMe


def create_test_about_me(
    db: Session,
    *,
    name: str | None = "Artur Ścibor",
    job_title: dict[str, str] | None = None,
    body_markdown: dict[str, str] | None = None,
) -> AboutMe:
    """Testy nie odpalają migracji (`Base.metadata.create_all` w conftest.py,
    nie `alembic upgrade head`), więc seed singletona z migracji nie zadziała —
    trzeba go stworzyć jawnie per test."""
    about_me = AboutMe(name=name, job_title=job_title, body_markdown=body_markdown)
    db.add(about_me)
    db.flush()
    return about_me
