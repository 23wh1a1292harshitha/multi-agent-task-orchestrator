"""add recipient_email to tasks

Revision ID: 54a32ec549c2
Revises: 28f847ed5465
Create Date: 2026-07-20 11:13:29.660724

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '54a32ec549c2'
down_revision: Union[str, None] = '28f847ed5465'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('tasks', sa.Column('recipient_email', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('tasks', 'recipient_email')