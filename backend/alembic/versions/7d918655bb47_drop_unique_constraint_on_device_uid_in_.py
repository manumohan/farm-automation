"""drop unique constraint on device_uid in devices table

Revision ID: 7d918655bb47
Revises: 5bf6fe2a7bdf
Create Date: 2025-06-26 13:37:40.700403

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7d918655bb47'
down_revision: Union[str, Sequence[str], None] = '5bf6fe2a7bdf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint('device_uid', 'devices', type_='unique')


def downgrade() -> None:
    """Downgrade schema."""
    op.create_unique_constraint('device_uid', 'devices', ['device_uid'])
