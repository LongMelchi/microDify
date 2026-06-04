"""replace provider_configs.api_key with auth_type + auth_config JSONB

Revision ID: d3e4f5a6b7c8
Revises: c1e2f3a4b5c6
Create Date: 2026-06-04 12:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision: str = "d3e4f5a6b7c8"
down_revision: Union[str, None] = "c1e2f3a4b5c6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add new columns (nullable first, then tighten after data migration).
    op.add_column(
        "provider_configs",
        sa.Column(
            "auth_type",
            sa.String(length=20),
            nullable=True,
        ),
    )
    op.add_column(
        "provider_configs",
        sa.Column(
            "auth_config",
            JSONB,
            nullable=True,
        ),
    )

    # 2. Migrate existing api_key data into auth_config JSONB.
    op.execute("""
        UPDATE provider_configs
        SET auth_type = 'bearer',
            auth_config = CASE
                WHEN api_key IS NOT NULL AND api_key != ''
                THEN jsonb_build_object('api_key', api_key)
                ELSE '{}'::jsonb
            END
    """)

    # 3. Set NOT NULL constraints + defaults after data migration.
    op.alter_column("provider_configs", "auth_type", nullable=False, server_default="bearer")
    op.alter_column("provider_configs", "auth_config", nullable=False, server_default=sa.text("'{}'::jsonb"))

    # 4. Drop the old api_key column.
    op.drop_column("provider_configs", "api_key")


def downgrade() -> None:
    # 1. Re-add api_key column (nullable initially).
    op.add_column(
        "provider_configs",
        sa.Column("api_key", sa.String(length=500), nullable=True),
    )

    # 2. Extract api_key back from auth_config JSONB.
    op.execute("""
        UPDATE provider_configs
        SET api_key = auth_config->>'api_key'
        WHERE auth_config ? 'api_key'
          AND auth_config->>'api_key' IS NOT NULL
          AND auth_config->>'api_key' != ''
    """)

    # 3. Make api_key NOT NULL after migration (rows without one get empty string).
    op.execute("UPDATE provider_configs SET api_key = '' WHERE api_key IS NULL")
    op.alter_column("provider_configs", "api_key", nullable=False)

    # 4. Drop new columns.
    op.drop_column("provider_configs", "auth_config")
    op.drop_column("provider_configs", "auth_type")
