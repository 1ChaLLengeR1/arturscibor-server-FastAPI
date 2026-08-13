"""work section: drop jobs/imagesme, add work + work_items (LinkedIn-style
experience, i18n JSONB) — docs/3.4-aboutme-home-section.md pkt. 4.2

Revision ID: 7fc71192432e
Revises: f8552ea2698b
Create Date: 2026-08-13 00:00:00

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import ARRAY, JSONB

# revision identifiers, used by Alembic.
revision: str = "7fc71192432e"
down_revision: Union[str, Sequence[str], None] = "f8552ea2698b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

employment_type_enum = sa.Enum(
    "full_time", "part_time", "contract", "b2b", "internship", "volunteer", name="employment_type"
)


def upgrade() -> None:
    # Jobs (płaskie stringi) / ImagesMe (niepowiązana galeria) — zastąpione przez
    # Work/WorkItem + logo per firma. Bez migracji danych, jak ustalone (docs/3.4 pkt. 7).
    op.drop_table("jobs")
    op.drop_table("imagesme")

    op.create_table(
        "work",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("company_name", sa.String(), nullable=False),
        sa.Column("logo_file_id", sa.Uuid(), nullable=True),
        sa.Column("numeric", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["logo_file_id"], ["files.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "work_items",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("work_id", sa.Uuid(), nullable=False),
        sa.Column("title", JSONB, nullable=False),
        sa.Column("employment_type", employment_type_enum, nullable=True),
        sa.Column("location", JSONB, nullable=True),
        sa.Column("date_from", sa.Date(), nullable=True),
        sa.Column("date_to", sa.Date(), nullable=True),
        sa.Column("body_markdown", JSONB, nullable=True),
        sa.Column("skills", ARRAY(sa.String()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["work_id"], ["work.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("work_items")
    op.drop_table("work")

    op.create_table(
        "imagesme",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("path", sa.String(), nullable=True),
        sa.Column("link", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "jobs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
