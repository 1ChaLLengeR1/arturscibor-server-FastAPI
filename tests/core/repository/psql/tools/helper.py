from sqlalchemy.orm import Session

from database.psql.models.tools import Tools


def create_test_tool(
    db: Session,
    *,
    name: str | None = "Python",
    information: str | None = "Backend language",
    progress: int | None = 80,
    numeric: int | None = 1,
    link: str | None = None,
) -> Tools:
    tool = Tools(name=name, information=information, progress=progress, numeric=numeric, link=link)
    db.add(tool)
    db.flush()
    return tool
