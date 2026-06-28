"""rename url to webhookurl

Revision ID: 9dc33d9b5574
Revises: 76d0212b1f42
Create Date: 2026-06-28 19:25:24.541840

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9dc33d9b5574'
down_revision: Union[str, Sequence[str], None] = '76d0212b1f42'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('payments', 'url', new_column_name='webhook_url')


def downgrade() -> None:
    """Downgrade schema."""
    pass
