"""create trades table

Revision ID: a1c3f5d7b9e2
Revises: e784a841747c
Create Date: 2026-10-19
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "a1c3f5d7b9e2"
down_revision = "e784a841747c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "trades",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("deriv_contract_id", sa.BigInteger(), nullable=False),
        sa.Column("symbol", sa.String(length=30), nullable=False),
        sa.Column("contract_type", sa.String(length=10), nullable=False),
        sa.Column("stake", sa.Numeric(18, 2), nullable=False),
        sa.Column("currency", sa.String(length=10), nullable=False),
        sa.Column("duration", sa.Integer(), nullable=False),
        sa.Column("duration_unit", sa.String(length=2), nullable=False),
        sa.Column("account_type", sa.String(length=10), nullable=False),
        sa.Column("status", sa.String(length=10), nullable=False),
        sa.Column("profit", sa.Numeric(18, 2), nullable=True),
        sa.Column("opened_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "deriv_contract_id", name="uq_trades_user_contract"),
    )
    op.create_index("ix_trades_user_id", "trades", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_trades_user_id", table_name="trades")
    op.drop_table("trades")