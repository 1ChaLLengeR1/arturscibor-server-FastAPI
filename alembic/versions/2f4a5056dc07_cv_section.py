"""cv section: FileType.DOCUMENT (PDF), curriculumvitae -> curriculum_vitae
singleton with file_id FK, seed (docs/3.4-aboutme-home-section.md pkt. 3/4.3/4.4)

Revision ID: 2f4a5056dc07
Revises: 7fc71192432e
Create Date: 2026-08-14 00:00:00

"""

import uuid
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2f4a5056dc07"
down_revision: Union[str, Sequence[str], None] = "7fc71192432e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Nowa wartość enuma — plik CV to teraz zwykły File, directory="cv".
    op.execute("ALTER TYPE file_type ADD VALUE IF NOT EXISTS 'document'")

    # Stary curriculumvitae (name/path/link, zapis na dysk mimo wszystko) zastąpiony
    # singletonem wskazującym na generyczny files (wzorzec B, jak Work.logo_file_id).
    # Bez migracji danych — nowy plik trzeba będzie wgrać ponownie przez file domain.
    op.drop_table("curriculumvitae")

    op.create_table(
        "curriculum_vitae",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("file_id", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["file_id"], ["files.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Singleton — jeden wiersz, file_id NULL dopóki admin nie wgra CV.
    op.execute(
        sa.text(
            "INSERT INTO curriculum_vitae (id, created_at, updated_at) "
            "SELECT :id, now(), now() WHERE NOT EXISTS (SELECT 1 FROM curriculum_vitae)"
        ).bindparams(id=str(uuid.uuid4()))
    )


def downgrade() -> None:
    op.drop_table("curriculum_vitae")

    op.create_table(
        "curriculumvitae",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("path", sa.String(), nullable=True),
        sa.Column("link", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    # Postgres nie pozwala usunąć wartości enuma bezpośrednio (DROP VALUE nie
    # istnieje) — zostawiamy 'document' w typie, downgrade i tak jest tu tylko
    # najlepszym wysiłkiem (nowe dane z tym file_type i tak by nie miały gdzie
    # wrócić po drop tabeli curriculum_vitae).
