"""contact rework: drop imagesmessage, add subject/phone/is_read/timestamps

Revision ID: bac0c456fb2a
Revises: 0a92dbff9d1c
Create Date: 2026-08-12 00:00:00

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "bac0c456fb2a"
down_revision: Union[str, Sequence[str], None] = "0a92dbff9d1c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_table("imagesmessage")

    op.add_column("contact", sa.Column("subject", sa.String(), nullable=True))
    op.add_column("contact", sa.Column("phone", sa.String(), nullable=True))
    op.add_column(
        "contact",
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "contact",
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.add_column(
        "contact",
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_column("contact", "updated_at")
    op.drop_column("contact", "created_at")
    op.drop_column("contact", "is_read")
    op.drop_column("contact", "phone")
    op.drop_column("contact", "subject")

    op.create_table(
        "imagesmessage",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("id_message", sa.Uuid(), nullable=True),
        sa.Column("path", sa.String(), nullable=True),
        sa.Column("link", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["id_message"], ["contact.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
