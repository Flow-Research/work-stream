"""Initial schema migration.

Revision ID: 001_initial_schema
Revises: 
Create Date: 2025-01-08

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('wallet_address', sa.String(42), nullable=False, unique=True, index=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('country', sa.String(2), nullable=False),
        sa.Column('national_id_hash', sa.String(64), nullable=True),
        sa.Column('id_verified', sa.Boolean(), default=False, nullable=False),
        sa.Column('id_verified_at', sa.DateTime(), nullable=True),
        sa.Column('id_verified_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('skills', postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('reputation_score', sa.Integer(), default=0, nullable=False),
        sa.Column('reputation_tier', sa.String(20), default='new', nullable=False),
        sa.Column('tasks_completed', sa.Integer(), default=0, nullable=False),
        sa.Column('tasks_approved', sa.Integer(), default=0, nullable=False),
        sa.Column('disputes_won', sa.Integer(), default=0, nullable=False),
        sa.Column('disputes_lost', sa.Integer(), default=0, nullable=False),
        sa.Column('is_admin', sa.Boolean(), default=False, nullable=False),
        sa.Column('is_banned', sa.Boolean(), default=False, nullable=False),
        sa.Column('banned_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    # Create tasks table
    op.create_table(
        'tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('description_html', sa.Text(), nullable=True),
        sa.Column('research_question', sa.Text(), nullable=False),
        sa.Column('background_context', sa.Text(), nullable=True),
        sa.Column('methodology_notes', sa.Text(), nullable=True),
        sa.Column('expected_outcomes', postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column('references', postgresql.JSONB(), nullable=True),
        sa.Column('attachments', postgresql.JSONB(), nullable=True),
        sa.Column('client_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('status', sa.String(20), default='draft', index=True, nullable=False),
        sa.Column('total_budget_cngn', sa.Numeric(18, 2), nullable=False),
        sa.Column('escrow_tx_hash', sa.String(66), nullable=True),
        sa.Column('escrow_contract_task_id', sa.Integer(), nullable=True),
        sa.Column('skills_required', postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column('deadline', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column('funded_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
    )

    # Create subtasks table
    op.create_table(
        'subtasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('task_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tasks.id'), nullable=False, index=True),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('description_html', sa.Text(), nullable=True),
        sa.Column('deliverables', postgresql.JSONB(), nullable=True),
        sa.Column('acceptance_criteria', postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column('references', postgresql.JSONB(), nullable=True),
        sa.Column('attachments', postgresql.JSONB(), nullable=True),
        sa.Column('example_output', sa.Text(), nullable=True),
        sa.Column('tools_required', postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column('estimated_hours', sa.Numeric(5, 2), nullable=True),
        sa.Column('subtask_type', sa.String(50), nullable=False),
        sa.Column('sequence_order', sa.Integer(), nullable=False),
        sa.Column('budget_allocation_percent', sa.Numeric(5, 2), nullable=False),
        sa.Column('budget_cngn', sa.Numeric(18, 2), nullable=False),
        sa.Column('status', sa.String(20), default='open', index=True, nullable=False),
        sa.Column('claimed_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True, index=True),
        sa.Column('claimed_at', sa.DateTime(), nullable=True),
        sa.Column('collaborators', postgresql.ARRAY(postgresql.UUID(as_uuid=True)), nullable=True),
        sa.Column('collaborator_splits', postgresql.ARRAY(sa.Numeric(5, 2)), nullable=True),
        sa.Column('submitted_at', sa.DateTime(), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('auto_approved', sa.Boolean(), default=False, nullable=False),
        sa.Column('deadline', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    # Create submissions table
    op.create_table(
        'submissions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('subtask_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('subtasks.id'), nullable=False, index=True),
        sa.Column('submitted_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('content_summary', sa.Text(), nullable=True),
        sa.Column('artifact_ipfs_hash', sa.String(64), nullable=True),
        sa.Column('artifact_type', sa.String(50), nullable=True),
        sa.Column('artifact_on_chain_hash', sa.String(66), nullable=True),
        sa.Column('artifact_on_chain_tx', sa.String(66), nullable=True),
        sa.Column('status', sa.String(20), default='pending', nullable=False),
        sa.Column('review_notes', sa.Text(), nullable=True),
        sa.Column('reviewed_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(), nullable=True),
        sa.Column('payment_tx_hash', sa.String(66), nullable=True),
        sa.Column('payment_amount_cngn', sa.Numeric(18, 2), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    # Create artifacts table
    op.create_table(
        'artifacts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('task_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tasks.id'), nullable=False, index=True),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('artifact_type', sa.String(50), nullable=False),
        sa.Column('ipfs_hash', sa.String(64), nullable=False),
        sa.Column('on_chain_hash', sa.String(66), nullable=True),
        sa.Column('on_chain_tx', sa.String(66), nullable=True),
        sa.Column('schema_version', sa.String(20), nullable=True),
        sa.Column('contributors', postgresql.ARRAY(postgresql.UUID(as_uuid=True)), nullable=False),
        sa.Column('contributor_shares', postgresql.ARRAY(sa.Numeric(5, 2)), nullable=False),
        sa.Column('total_earnings_cngn', sa.Numeric(18, 2), default=0, nullable=False),
        sa.Column('is_listed', sa.Boolean(), default=False, nullable=False),
        sa.Column('listed_price_cngn', sa.Numeric(18, 2), nullable=True),
        sa.Column('royalty_cap_multiplier', sa.Numeric(3, 1), default=5.0, nullable=False),
        sa.Column('royalty_expiry_years', sa.Integer(), default=3, nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    # Create artifact_purchases table
    op.create_table(
        'artifact_purchases',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('artifact_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('artifacts.id'), nullable=False),
        sa.Column('buyer_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('buyer_wallet', sa.String(42), nullable=True),
        sa.Column('amount_cngn', sa.Numeric(18, 2), nullable=False),
        sa.Column('platform_fee_cngn', sa.Numeric(18, 2), nullable=False),
        sa.Column('payment_tx_hash', sa.String(66), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    # Create disputes table
    op.create_table(
        'disputes',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('subtask_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('subtasks.id'), nullable=False),
        sa.Column('raised_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('status', sa.String(20), default='open', nullable=False),
        sa.Column('resolution', sa.Text(), nullable=True),
        sa.Column('resolved_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('winner_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('disputes')
    op.drop_table('artifact_purchases')
    op.drop_table('artifacts')
    op.drop_table('submissions')
    op.drop_table('subtasks')
    op.drop_table('tasks')
    op.drop_table('users')
