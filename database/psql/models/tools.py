import uuid

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Uuid

from database.psql.base import Base


class Tools(Base):
    __tablename__ = "tools"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str | None] = mapped_column(String)
    information: Mapped[str | None] = mapped_column(String)
    progress: Mapped[str | None] = mapped_column(String)
    numeric: Mapped[str | None] = mapped_column(String)
    link: Mapped[str | None] = mapped_column(String)
    path_image: Mapped[str | None] = mapped_column(String)
    link_image: Mapped[str | None] = mapped_column(String)
