"""add provider_models table

Revision ID: e7f8a9b0c1d2
Revises: d3e4f5a6b7c8
Create Date: 2026-06-04 14:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = "e7f8a9b0c1d2"
down_revision: Union[str, None] = "d3e4f5a6b7c8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "provider_models",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column(
            "provider_config_id",
            UUID(as_uuid=True),
            sa.ForeignKey("provider_configs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("model_name", sa.String(length=100), nullable=False),
        sa.Column("display_name", sa.String(length=200), nullable=True),
        sa.Column("supports_chat", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("supports_embedding", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("supports_vision", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("max_tokens", sa.Integer(), nullable=True),
        sa.Column("default_temperature", sa.Float(), nullable=True),
        sa.Column("input_cost_per_1k", sa.Float(), nullable=True),
        sa.Column("output_cost_per_1k", sa.Float(), nullable=True),
        sa.Column("is_enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("provider_config_id", "model_name", name="uq_provider_model"),
    )
    # Composite index for listing models by provider sorted by order+name.
    op.create_index(
        "ix_provider_models_provider_sort",
        "provider_models",
        ["provider_config_id", "sort_order", "model_name"],
        unique=False,
    )
    # Index for filtering enabled models.
    op.create_index(
        "ix_provider_models_provider_enabled",
        "provider_models",
        ["provider_config_id", "is_enabled"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_provider_models_provider_enabled", table_name="provider_models")
    op.drop_index("ix_provider_models_provider_sort", table_name="provider_models")
    op.drop_table("provider_models")
