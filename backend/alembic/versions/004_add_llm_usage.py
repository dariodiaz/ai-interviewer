"""Add LLM usage tracking table.

Revision ID: 004_add_llm_usage
Revises: 003_add_token_expiration
Create Date: 2026-01-14

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '004_add_llm_usage'
down_revision = '003_add_token_expiration'
branch_labels = None
depends_on = None


def upgrade():
    """Create llm_usage table."""
    op.create_table(
        'llm_usage',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('interview_id', sa.Integer(), nullable=False),
        sa.Column('agent_name', sa.String(), nullable=False),
        sa.Column('model', sa.String(), nullable=False),
        sa.Column('prompt_tokens', sa.Integer(), nullable=False),
        sa.Column('completion_tokens', sa.Integer(), nullable=False),
        sa.Column('total_tokens', sa.Integer(), nullable=False),
        sa.Column('estimated_cost', sa.Float(), nullable=False),
        sa.Column('cached', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['interview_id'], ['interviews.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('ix_llm_usage_interview_id', 'llm_usage', ['interview_id'])
    op.create_index('ix_llm_usage_agent_name', 'llm_usage', ['agent_name'])


def downgrade():
    """Drop llm_usage table."""
    op.drop_index('ix_llm_usage_agent_name', table_name='llm_usage')
    op.drop_index('ix_llm_usage_interview_id', table_name='llm_usage')
    op.drop_table('llm_usage')
