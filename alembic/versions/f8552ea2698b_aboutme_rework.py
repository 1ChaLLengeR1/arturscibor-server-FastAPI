"""aboutme rework: drop informationme/readmore duplicates, aboutme -> about_me
with JSONB job_title/body_markdown (i18n), add about_me_images carousel
(docs/3.4-aboutme-home-section.md, docs/7-i18n-section.md)

Revision ID: f8552ea2698b
Revises: d356a8a518d6
Create Date: 2026-08-13 00:00:00

"""

import uuid
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision: str = "f8552ea2698b"
down_revision: Union[str, Sequence[str], None] = "d356a8a518d6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_table("informationme")
    op.drop_table("readmore")

    op.rename_table("aboutme", "about_me")

    # job -> job_title (JSONB, backfill jako pl — jedyny język, jaki dotąd istniał).
    op.add_column("about_me", sa.Column("job_title", JSONB, nullable=True))
    op.execute(
        "UPDATE about_me SET job_title = "
        "CASE WHEN job IS NOT NULL THEN jsonb_build_object('pl', job) ELSE NULL END"
    )
    op.drop_column("about_me", "job")

    # information -> body_markdown (JSONB, backfill jako pl).
    op.add_column("about_me", sa.Column("body_markdown", JSONB, nullable=True))
    op.execute(
        "UPDATE about_me SET body_markdown = "
        "CASE WHEN information IS NOT NULL THEN jsonb_build_object('pl', information) ELSE NULL END"
    )
    op.drop_column("about_me", "information")

    # path_image/link_image — zastąpione przez about_me_images (generyczny file domain).
    op.drop_column("about_me", "path_image")
    op.drop_column("about_me", "link_image")

    op.add_column(
        "about_me",
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.add_column(
        "about_me",
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "about_me_images",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("about_me_id", sa.Uuid(), nullable=False),
        sa.Column("file_id", sa.Uuid(), nullable=False),
        sa.Column("sort_order", sa.Integer(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["about_me_id"], ["about_me.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["file_id"], ["files.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("file_id"),
    )

    # Singleton — dokładnie jeden wiersz. Jeśli `aboutme` miało już realny wiersz,
    # rename + ALTER go zachowuje; ten INSERT tylko zabezpiecza pustą (np. testową) bazę.
    op.execute(
        sa.text(
            "INSERT INTO about_me (id, created_at, updated_at) "
            "SELECT :id, now(), now() WHERE NOT EXISTS (SELECT 1 FROM about_me)"
        ).bindparams(id=str(uuid.uuid4()))
    )


def downgrade() -> None:
    op.drop_table("about_me_images")

    op.drop_column("about_me", "updated_at")
    op.drop_column("about_me", "created_at")

    op.add_column("about_me", sa.Column("link_image", sa.String(), nullable=True))
    op.add_column("about_me", sa.Column("path_image", sa.String(), nullable=True))

    op.add_column("about_me", sa.Column("information", sa.String(), nullable=True))
    op.execute("UPDATE about_me SET information = body_markdown->>'pl'")
    op.drop_column("about_me", "body_markdown")

    op.add_column("about_me", sa.Column("job", sa.String(), nullable=True))
    op.execute("UPDATE about_me SET job = job_title->>'pl'")
    op.drop_column("about_me", "job_title")

    op.rename_table("about_me", "aboutme")

    op.create_table(
        "readmore",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("information", sa.String(), nullable=True),
        sa.Column("numeric", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "informationme",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("information", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
