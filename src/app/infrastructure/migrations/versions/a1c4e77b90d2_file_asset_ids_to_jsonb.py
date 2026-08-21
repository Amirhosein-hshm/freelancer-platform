"""file asset id columns to jsonb

Revision ID: a1c4e77b90d2
Revises: c7135dc495b6
Create Date: 2026-08-19 10:00:00.000000

``ticket_messages.attachment_file_asset_ids`` and ``project_deliveries.file_asset_ids`` were
declared as ``JSON``. ``IProjectDeliveryRepository.list_by_file_asset_id`` and
``ITicketMessageRepository.list_by_file_asset_id`` query them with a containment predicate,
which plain ``JSON`` does not support: SQLAlchemy degrades it to ``LIKE``, and Postgres
rejects that with ``operator does not exist: json ~~ text``. Both methods therefore raised a
500 at runtime, breaking file-access authorization in ``DomainFileAccessPolicy``. ``JSONB``
supports the containment operator natively.
"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1c4e77b90d2"
down_revision: Union[str, None] = "c7135dc495b6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE ticket_messages "
        "ALTER COLUMN attachment_file_asset_ids TYPE JSONB "
        "USING attachment_file_asset_ids::text::jsonb"
    )
    op.execute(
        "ALTER TABLE project_deliveries "
        "ALTER COLUMN file_asset_ids TYPE JSONB "
        "USING file_asset_ids::text::jsonb"
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE ticket_messages "
        "ALTER COLUMN attachment_file_asset_ids TYPE JSON "
        "USING attachment_file_asset_ids::text::json"
    )
    op.execute(
        "ALTER TABLE project_deliveries "
        "ALTER COLUMN file_asset_ids TYPE JSON USING file_asset_ids::text::json"
    )
