"""Add token expiration

Revision ID: 003_add_token_expiration
Revises: 002_add_composite_indexes
Create Date: 2026-01-13 21:46:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003_add_token_expiration'
down_revision = '002_add_composite_indexes'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add token_expires_at column to interviews table."""
    op.add_column(
        'interviews',
        sa.Column('token_expires_at', sa.DateTime(timezone=True), nullable=True)
    )


def downgrade() -> None:
    """Remove token_expires_at column from interviews table."""
    op.drop_column('interviews', 'token_expires_at')
