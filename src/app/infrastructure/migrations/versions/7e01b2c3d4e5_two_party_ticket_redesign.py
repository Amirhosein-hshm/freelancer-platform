"""two-party ticket redesign (drop participant model)

Revision ID: 7e01b2c3d4e5
Revises: 3f9b1c2d5e8a
Create Date: 2026-08-20 00:00:00.000000

Tickets become strictly two-party conversations (creator + target). The old
``ticket_participants`` table and the ``assigned_to_user_id`` column (a single ad-hoc
assignee that never matched the participant model) are removed in favour of a dedicated
``tickets.target_user_id`` column holding the second party. The ``TicketStatus`` enum is
also pruned to OPEN / CLOSED / ARCHIVED, but because statuses are stored as plain strings no
data migration is required — any legacy ``in_progress`` / ``waiting_*`` rows simply retain
their string until edited (the code no longer produces them).
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "7e01b2c3d4e5"
down_revision: Union[str, None] = "3f9b1c2d5e8a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # tickets: assigned_to_user_id (nullable, ad-hoc assignee) -> target_user_id (NOT NULL second party)
    op.drop_index("ix_tickets_assigned_to_user_id", table_name="tickets")
    op.alter_column(
        "tickets",
        "assigned_to_user_id",
        new_column_name="target_user_id",
        existing_type=sa.String(length=36),
        existing_nullable=True,
        nullable=False,
    )
    op.create_index("ix_tickets_target_user_id", "tickets", ["target_user_id"], unique=False)

    # drop the participant model; a ticket is now just its two parties
    op.drop_index("ix_ticket_participants_user_id", table_name="ticket_participants")
    op.drop_index("ix_ticket_participants_ticket_id", table_name="ticket_participants")
    op.drop_table("ticket_participants")
    op.drop_index("ix_tickets_related_project_id", table_name="tickets")
    op.drop_index("ix_tickets_related_category_id", table_name="tickets")
    op.drop_constraint("fk_tickets_related_project_id_projects", "tickets", type_="foreignkey")
    op.drop_constraint("fk_tickets_related_category_id_categories", "tickets", type_="foreignkey")
    op.drop_column("tickets", "related_project_id")
    op.drop_column("tickets", "related_category_id")


def downgrade() -> None:
    op.add_column("tickets", sa.Column("related_project_id", sa.String(length=36), nullable=True))
    op.add_column("tickets", sa.Column("related_category_id", sa.String(length=36), nullable=True))
    op.create_foreign_key(
        "fk_tickets_related_project_id_projects", "tickets", "projects", ["related_project_id"], ["id"]
    )
    op.create_foreign_key(
        "fk_tickets_related_category_id_categories", "tickets", "categories", ["related_category_id"], ["id"]
    )
    op.create_index("ix_tickets_related_project_id", "tickets", ["related_project_id"], unique=False)
    op.create_index("ix_tickets_related_category_id", "tickets", ["related_category_id"], unique=False)
    op.create_table(
        "ticket_participants",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("ticket_id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("participant_role", sa.String(length=20), nullable=False),
        sa.Column("joined_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("left_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["ticket_id"], ["tickets.id"], name=op.f("fk_ticket_participants_ticket_id_tickets")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_ticket_participants")),
    )
    op.create_index(op.f("ix_ticket_participants_ticket_id"), "ticket_participants", ["ticket_id"], unique=False)
    op.create_index(op.f("ix_ticket_participants_user_id"), "ticket_participants", ["user_id"], unique=False)

    op.drop_index("ix_tickets_target_user_id", table_name="tickets")
    op.alter_column(
        "tickets",
        "target_user_id",
        new_column_name="assigned_to_user_id",
        existing_type=sa.String(length=36),
        existing_nullable=False,
        nullable=True,
    )
    op.create_index(op.f("ix_tickets_assigned_to_user_id"), "tickets", ["assigned_to_user_id"], unique=False)
