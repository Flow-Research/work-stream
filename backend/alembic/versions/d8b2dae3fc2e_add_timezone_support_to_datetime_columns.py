"""add_timezone_support_to_datetime_columns

Revision ID: d8b2dae3fc2e
Revises: 001_initial_schema
Create Date: 2026-01-08 12:27:10.407593

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'd8b2dae3fc2e'
down_revision: Union[str, None] = '001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Convert datetime columns to TIMESTAMP WITH TIME ZONE for tasks table
    op.execute('ALTER TABLE tasks ALTER COLUMN deadline TYPE TIMESTAMP WITH TIME ZONE')
    op.execute('ALTER TABLE tasks ALTER COLUMN funded_at TYPE TIMESTAMP WITH TIME ZONE')
    op.execute('ALTER TABLE tasks ALTER COLUMN completed_at TYPE TIMESTAMP WITH TIME ZONE')
    
    # Convert datetime columns to TIMESTAMP WITH TIME ZONE for subtasks table
    op.execute('ALTER TABLE subtasks ALTER COLUMN deadline TYPE TIMESTAMP WITH TIME ZONE')
    op.execute('ALTER TABLE subtasks ALTER COLUMN claimed_at TYPE TIMESTAMP WITH TIME ZONE')
    op.execute('ALTER TABLE subtasks ALTER COLUMN submitted_at TYPE TIMESTAMP WITH TIME ZONE')
    op.execute('ALTER TABLE subtasks ALTER COLUMN approved_at TYPE TIMESTAMP WITH TIME ZONE')


def downgrade() -> None:
    # Revert to TIMESTAMP WITHOUT TIME ZONE for tasks table
    op.execute('ALTER TABLE tasks ALTER COLUMN deadline TYPE TIMESTAMP WITHOUT TIME ZONE')
    op.execute('ALTER TABLE tasks ALTER COLUMN funded_at TYPE TIMESTAMP WITHOUT TIME ZONE')
    op.execute('ALTER TABLE tasks ALTER COLUMN completed_at TYPE TIMESTAMP WITHOUT TIME ZONE')
    
    # Revert to TIMESTAMP WITHOUT TIME ZONE for subtasks table
    op.execute('ALTER TABLE subtasks ALTER COLUMN deadline TYPE TIMESTAMP WITHOUT TIME ZONE')
    op.execute('ALTER TABLE subtasks ALTER COLUMN claimed_at TYPE TIMESTAMP WITHOUT TIME ZONE')
    op.execute('ALTER TABLE subtasks ALTER COLUMN submitted_at TYPE TIMESTAMP WITHOUT TIME ZONE')
    op.execute('ALTER TABLE subtasks ALTER COLUMN approved_at TYPE TIMESTAMP WITHOUT TIME ZONE')
