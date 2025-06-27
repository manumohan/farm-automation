"""update_section_model_with_new_fields

Revision ID: 2986dd0a280c
Revises: f9ddd71613a2
Create Date: 2025-06-26 11:16:10.060897

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2986dd0a280c'
down_revision: Union[str, Sequence[str], None] = 'f9ddd71613a2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add missing columns to sections table (skip if already added)
    # op.add_column('sections', sa.Column('section_incharge_name', sa.String(length=255), nullable=True))
    # op.add_column('sections', sa.Column('notes', sa.String(length=1000), nullable=True))
    # op.add_column('sections', sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0'))
    
    # Modify existing columns (MySQL requires existing type)
    op.alter_column('sections', 'area', existing_type=sa.Float(), nullable=False)
    op.alter_column('sections', 'description', existing_type=sa.String(length=255), type_=sa.String(length=500))


def downgrade() -> None:
    """Downgrade schema."""
    # Drop new columns (skip if already dropped)
    # op.drop_column('sections', 'is_deleted')
    # op.drop_column('sections', 'notes')
    # op.drop_column('sections', 'section_incharge_name')
    
    # Revert column modifications
    op.alter_column('sections', 'area', existing_type=sa.Float(), nullable=True)
    op.alter_column('sections', 'description', existing_type=sa.String(length=500), type_=sa.String(length=255))
