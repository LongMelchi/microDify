"""add provider health status tracking fields

Revision ID: f9a0b1c2d3e4
Revises: e7f8a9b0c1d2
Create Date: 2026-06-04 16:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f9a0b1c2d3e4"
down_revision: Union[str, None] = "e7f8a9b0c1d2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "provider_configs",
        sa.Column(
            "health_status",
            sa.String(length=20),
            nullable=False,
            server_default="unknown",
        ),
    )
    op.add_column(
        "provider_configs",
        sa.Column("last_health_check_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "provider_configs",
        sa.Column(
            "consecutive_failures",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )
    op.add_column(
        "provider_configs",
        sa.Column("last_error_message", sa.Text(), nullable=True),
    )
    op.create_index(
        "ix_provider_configs_health_status",
        "provider_configs",
        ["health_status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_provider_configs_health_status", table_name="provider_configs")
    op.drop_column("provider_configs", "last_error_message")
    op.drop_column("provider_configs", "consecutive_failures")
    op.drop_column("provider_configs", "last_health_check_at")
    op.drop_column("provider_configs", "health_status")
