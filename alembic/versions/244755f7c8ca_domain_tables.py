"""domain tables

Revision ID: 244755f7c8ca
Revises: a3352b2ed4c5
Create Date: 2026-08-12 00:00:00

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "244755f7c8ca"
down_revision: Union[str, Sequence[str], None] = "a3352b2ed4c5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "curriculumvitae",
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
    op.create_table(
        "imagesme",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("path", sa.String(), nullable=True),
        sa.Column("link", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "informationme",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("information", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "aboutme",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("job", sa.String(), nullable=True),
        sa.Column("information", sa.String(), nullable=True),
        sa.Column("path_image", sa.String(), nullable=True),
        sa.Column("link_image", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "readmore",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("information", sa.String(), nullable=True),
        sa.Column("numeric", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "tools",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("information", sa.String(), nullable=True),
        sa.Column("progress", sa.String(), nullable=True),
        sa.Column("numeric", sa.String(), nullable=True),
        sa.Column("link", sa.String(), nullable=True),
        sa.Column("path_image", sa.String(), nullable=True),
        sa.Column("link_image", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "projects",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name_project", sa.String(), nullable=True),
        sa.Column("short_description", sa.String(), nullable=True),
        sa.Column("file_path", sa.String(), nullable=True),
        sa.Column("file_link", sa.String(), nullable=True),
        sa.Column("completion_data", sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.Column("project_number", sa.Integer(), nullable=True),
        sa.Column("level_advanced", sa.String(), nullable=True),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("link_page", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "filesproject",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("id_project", sa.Uuid(), nullable=True),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("path", sa.String(), nullable=True),
        sa.Column("link", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["id_project"], ["projects.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "imagesproject",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("id_project", sa.Uuid(), nullable=True),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("path", sa.String(), nullable=True),
        sa.Column("link", sa.String(), nullable=True),
        sa.Column("type", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["id_project"], ["projects.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "technologiesproject",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("id_project", sa.Uuid(), nullable=True),
        sa.Column("name", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["id_project"], ["projects.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "contact",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("email", sa.String(), nullable=True),
        sa.Column("description", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "imagesmessage",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("id_message", sa.Uuid(), nullable=True),
        sa.Column("path", sa.String(), nullable=True),
        sa.Column("link", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["id_message"], ["contact.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("imagesmessage")
    op.drop_table("contact")
    op.drop_table("technologiesproject")
    op.drop_table("imagesproject")
    op.drop_table("filesproject")
    op.drop_table("projects")
    op.drop_table("tools")
    op.drop_table("readmore")
    op.drop_table("aboutme")
    op.drop_table("informationme")
    op.drop_table("imagesme")
    op.drop_table("jobs")
    op.drop_table("curriculumvitae")
