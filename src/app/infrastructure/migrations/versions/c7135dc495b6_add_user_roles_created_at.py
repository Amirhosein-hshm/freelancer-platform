"""add user_roles created_at

Revision ID: c7135dc495b6
Revises: 7b0f0b6ea8ea
Create Date: 2026-08-05 05:19:00.574035

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c7135dc495b6'
down_revision: Union[str, None] = '7b0f0b6ea8ea'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'user_roles',
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text('now()'),
        ),
    )
    op.alter_column('user_roles', 'created_at', server_default=None)


def downgrade() -> None:
    op.drop_column('user_roles', 'created_at')
