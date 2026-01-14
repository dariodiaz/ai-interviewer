"""Add composite index for interview queries

Revision ID: 002_add_composite_indexes
Revises: 001_initial_migration
Create Date: 2026-01-13 21:45:00

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '002_add_composite_indexes'
down_revision = '001_initial_migration'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add composite indexes for common query patterns."""
    # Composite index for filtering interviews by status and creation date
    op.create_index(
        'ix_interviews_status_created',
        'interviews',
        ['status', 'created_at'],
        unique=False
    )
    
    # Composite index for message queries by interview and timestamp
    op.create_index(
        'ix_messages_interview_timestamp',
        'messages',
        ['interview_id', 'timestamp'],
        unique=False
    )


def downgrade() -> None:
    """Remove composite indexes."""
    op.drop_index('ix_messages_interview_timestamp', table_name='messages')
    op.drop_index('ix_interviews_status_created', table_name='interviews')
