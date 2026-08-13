"""tools i18n: name/information -> JSONB {"lang": "text"} (docs/7-i18n-section.md)

Revision ID: d356a8a518d6
Revises: 3224b2caf509
Create Date: 2026-08-13 00:00:00

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision: str = "d356a8a518d6"
down_revision: Union[str, Sequence[str], None] = "3224b2caf509"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # COALESCE(name, '') — name było nullable w starym schemacie; nowy model
    # (Mapped[dict[str, str]], bez | None) wymaga zawsze co najmniej klucza "pl".
    op.alter_column(
        "tools",
        "name",
        existing_type=sa.String(),
        type_=JSONB,
        postgresql_using="jsonb_build_object('pl', COALESCE(name, ''))",
        nullable=False,
    )
    op.alter_column(
        "tools",
        "information",
        existing_type=sa.String(),
        type_=JSONB,
        postgresql_using="CASE WHEN information IS NOT NULL "
        "THEN jsonb_build_object('pl', information) ELSE NULL END",
        nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "tools",
        "information",
        existing_type=JSONB,
        type_=sa.String(),
        postgresql_using="information->>'pl'",
        nullable=True,
    )
    op.alter_column(
        "tools",
        "name",
        existing_type=JSONB,
        type_=sa.String(),
        postgresql_using="name->>'pl'",
        nullable=True,
    )
