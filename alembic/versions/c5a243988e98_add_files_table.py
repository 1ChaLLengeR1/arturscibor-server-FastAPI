"""add files table: local S3-like storage for projects/aboutme/tools uploads

Revision ID: c5a243988e98
Revises: bac0c456fb2a
Create Date: 2026-08-13 00:00:00

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c5a243988e98"
down_revision: Union[str, Sequence[str], None] = "bac0c456fb2a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

file_type_enum = sa.Enum("photo", "video", name="file_type")
file_status_enum = sa.Enum("pending", "completed", "failed", "confirmed", name="file_status")


def upgrade() -> None:
    # Nie tworzymy typów jawnie — create_table samo je wystawia (Enum column ->
    # auto CREATE TYPE), jawny .create() tutaj dubluje je w trybie `--sql`.
    op.create_table(
        "files",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("original_name", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("size", sa.BigInteger(), nullable=False),
        sa.Column("mime_type", sa.String(), nullable=True),
        sa.Column("url", sa.String(), nullable=True),
        sa.Column("directory", sa.String(), nullable=False),
        sa.Column("file_type", file_type_enum, nullable=False),
        sa.Column("status", file_status_enum, nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index("ix_files_status", "files", ["status"])
    op.create_index("ix_files_file_type", "files", ["file_type"])
    op.create_index("ix_files_directory", "files", ["directory"])


def downgrade() -> None:
    op.drop_index("ix_files_directory", table_name="files")
    op.drop_index("ix_files_file_type", table_name="files")
    op.drop_index("ix_files_status", table_name="files")
    op.drop_table("files")

    file_status_enum.drop(op.get_bind(), checkfirst=True)
    file_type_enum.drop(op.get_bind(), checkfirst=True)
