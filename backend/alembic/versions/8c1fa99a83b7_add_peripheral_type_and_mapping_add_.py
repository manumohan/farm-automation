"""add peripheral type and mapping, add available_gpio_pins to device

Revision ID: 8c1fa99a83b7
Revises: 7d918655bb47
Create Date: 2025-06-26 14:01:14.769115

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8c1fa99a83b7'
down_revision: Union[str, Sequence[str], None] = '7d918655bb47'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('peripheral_types',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('scope', sa.String(length=20), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_peripheral_types_id'), 'peripheral_types', ['id'], unique=False)
    op.create_table('peripheral_mappings',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('device_id', sa.Integer(), nullable=False),
    sa.Column('farm_id', sa.Integer(), nullable=True),
    sa.Column('section_id', sa.Integer(), nullable=True),
    sa.Column('peripheral_type_id', sa.Integer(), nullable=False),
    sa.Column('gpio_pin', sa.Integer(), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['device_id'], ['devices.id'], ),
    sa.ForeignKeyConstraint(['farm_id'], ['farms.id'], ),
    sa.ForeignKeyConstraint(['peripheral_type_id'], ['peripheral_types.id'], ),
    sa.ForeignKeyConstraint(['section_id'], ['sections.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_peripheral_mappings_id'), 'peripheral_mappings', ['id'], unique=False)
    op.add_column('devices', sa.Column('available_gpio_pins', sa.String(length=255), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('devices', 'available_gpio_pins')
    op.drop_index(op.f('ix_peripheral_mappings_id'), table_name='peripheral_mappings')
    op.drop_table('peripheral_mappings')
    op.drop_index(op.f('ix_peripheral_types_id'), table_name='peripheral_types')
    op.drop_table('peripheral_types')
    # ### end Alembic commands ###
