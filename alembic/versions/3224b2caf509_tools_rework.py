"""tools rework: drop path_image/link_image (replaced by files), add
timestamps, fix progress/numeric to Integer, add tools_images join table

Revision ID: 3224b2caf509
Revises: c5a243988e98
Create Date: 2026-08-13 00:00:00

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "3224b2caf509"
down_revision: Union[str, Sequence[str], None] = "c5a243988e98"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("tools", "path_image")
    op.drop_column("tools", "link_image")

    op.alter_column("tools", "progress", type_=sa.Integer(), postgresql_using="progress::integer")
    op.alter_column("tools", "numeric", type_=sa.Integer(), postgresql_using="numeric::integer")

    op.add_column(
        "tools",
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.add_column(
        "tools",
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "tools_images",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tool_id", sa.Uuid(), nullable=False),
        sa.Column("file_id", sa.Uuid(), nullable=False),
        sa.Column("sort_order", sa.Integer(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["tool_id"], ["tools.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["file_id"], ["files.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("file_id"),
    )


def downgrade() -> None:
    op.drop_table("tools_images")

    op.drop_column("tools", "updated_at")
    op.drop_column("tools", "created_at")

    op.alter_column("tools", "numeric", type_=sa.String(), postgresql_using="numeric::text")
    op.alter_column("tools", "progress", type_=sa.String(), postgresql_using="progress::text")

    op.add_column("tools", sa.Column("link_image", sa.String(), nullable=True))
    op.add_column("tools", sa.Column("path_image", sa.String(), nullable=True))
