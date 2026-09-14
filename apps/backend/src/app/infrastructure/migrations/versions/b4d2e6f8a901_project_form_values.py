"""persist project dynamic form values"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "b4d2e6f8a901"
down_revision: Union[str, None] = "7e01b2c3d4e5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column("projects", sa.Column("form_values", sa.JSON(), nullable=False, server_default="[]"))
    op.alter_column("projects", "form_values", server_default=None)

def downgrade() -> None:
    op.drop_column("projects", "form_values")
