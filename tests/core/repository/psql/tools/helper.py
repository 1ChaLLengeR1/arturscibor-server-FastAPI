from sqlalchemy.orm import Session

from database.psql.models.tools import Tools

_UNSET = object()


def create_test_tool(
    db: Session,
    *,
    name: dict[str, str] | None = None,
    information: dict[str, str] | None = _UNSET,
    progress: int | None = 80,
    numeric: int | None = 1,
    link: str | None = None,
) -> Tools:
    tool = Tools(
        name=name or {"pl": "Python", "en": "Python"},
        information={"pl": "Backend language", "en": "Backend language"} if information is _UNSET else information,
        progress=progress,
        numeric=numeric,
        link=link,
    )
    db.add(tool)
    db.flush()
    return tool
