"""init

Revision ID: 918d7af4e5de
Revises: 
Create Date: 2026-03-02 02:52:07.843538

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '918d7af4e5de'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), unique=True, primary_key=True, autoincrement=False),
        sa.Column("username", sa.String(length=255), unique=True, nullable=False),
        sa.Column("first_name", sa.String(length=255), nullable=True),
        sa.Column("last_name", sa.String(length=255), nullable=True),
        sa.Column("language_code", sa.String(length=100), nullable=True),
        sa.Column("notify_settings", sa.JSON()),
        sa.Column("created_at", sa.TIMESTAMP, server_default=sa.func.now()),
        sa.Column("updated_at", sa.TIMESTAMP, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_table(
        "daily_tasks",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("start_dt", sa.DateTime(), nullable=False),
        sa.Column("end_dt", sa.DateTime(), nullable=False),
        sa.Column("state", sa.String(50), nullable=False, default="created"),
        sa.Column("real_start_dt", sa.DateTime(), nullable=True),
        sa.Column("real_end_dt", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP, server_default=sa.func.now()),
        sa.Column("updated_at", sa.TIMESTAMP, server_default=sa.func.now(), onupdate=sa.func.now()),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("daily_tasks")
    op.drop_table("users")
