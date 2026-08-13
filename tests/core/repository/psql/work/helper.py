from sqlalchemy.orm import Session

from database.psql.models.work import Work


def create_test_work(db: Session, *, company_name: str = "SPINETIME", numeric: int | None = 1) -> Work:
    work = Work(company_name=company_name, numeric=numeric)
    db.add(work)
    db.flush()
    return work
