"""add provider_configs table and users.role/status columns

Brings the schema back in sync with the ORM models after two drifts:

* ``app.provider.models.ProviderConfig`` was added (LLM provider connections)
  but never migrated.
* ``app.auth.models.User`` gained ``role`` and ``status`` columns.

Also fixes ``users.username`` — the initial migration created it as a UNIQUE
index, but the model declares a plain (non-unique) index.

Revision ID: c1e2f3a4b5c6
Revises: bd71cd6d35f1
Create Date: 2026-06-03 16:45:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c1e2f3a4b5c6"
down_revision: Union[str, None] = "bd71cd6d35f1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── users: add role / status, fix username index ──────────────────────
    op.add_column(
        "users",
        sa.Column(
            "role",
            sa.String(length=20),
            nullable=False,
            server_default="developer",
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=False,
            server_default="active",
        ),
    )
    # Model declares username as a plain index; the initial migration made it
    # UNIQUE. Recreate it non-unique to match the model.
    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=False)
    # Supports list_users filtering by status + ordering by created_at DESC.
    op.create_index(
        "ix_users_status_created_at", "users", ["status", "created_at"], unique=False
    )

    # ── provider_configs ──────────────────────────────────────────────────
    op.create_table(
        "provider_configs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("provider_type", sa.String(length=20), nullable=False),
        sa.Column("base_url", sa.String(length=500), nullable=False),
        sa.Column("api_key", sa.String(length=500), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column("last_called_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "is_deleted",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
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
    )
    op.create_index(
        op.f("ix_provider_configs_provider_type"),
        "provider_configs",
        ["provider_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_provider_configs_is_active"),
        "provider_configs",
        ["is_active"],
        unique=False,
    )
    # Supports list_providers: WHERE is_deleted = false ORDER BY created_at DESC.
    op.create_index(
        "ix_provider_configs_is_deleted_created_at",
        "provider_configs",
        ["is_deleted", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_provider_configs_is_deleted_created_at", table_name="provider_configs"
    )
    op.drop_index(
        op.f("ix_provider_configs_is_active"), table_name="provider_configs"
    )
    op.drop_index(
        op.f("ix_provider_configs_provider_type"), table_name="provider_configs"
    )
    op.drop_table("provider_configs")

    op.drop_index("ix_users_status_created_at", table_name="users")
    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)
    op.drop_column("users", "status")
    op.drop_column("users", "role")
