"""freelancer level redesign to fixed enum

Revision ID: 3f9b1c2d5e8a
Revises: a1c4e77b90d2
Create Date: 2026-08-20 00:00:00.000000

Freelancer levels were a configurable table (``freelancer_levels``) referenced by
``freelancer_profiles.current_level_id`` and ``freelancer_level_history.old_level_id`` /
``new_level_id``. The 7d redesign fixes the set of levels to a closed enum
(``FreelancerLevelEnum``: JUNIOR / MID_LEVEL / SENIOR) and evaluates eligibility with a
hierarchical ``>=`` rule, so the table and its FK columns are replaced by plain enum-string
columns, and ``projects.required_level`` is introduced for eligibility filtering.

Because the level set is now fixed, existing rows are reset to ``NULL`` (profiles) and the
history table is kept but its level columns become free-form enum strings; no attempt is
made to migrate old level rows to the new enum — admins re-assign levels.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "3f9b1c2d5e8a"
down_revision: Union[str, None] = "a1c4e77b90d2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # freelancer_profiles: current_level_id (FK to freelancer_levels) -> current_level enum string
    op.drop_constraint(
        "fk_freelancer_profiles_current_level_id_freelancer_levels",
        "freelancer_profiles",
        type_="foreignkey",
    )
    op.drop_index("ix_freelancer_profiles_current_level_id", table_name="freelancer_profiles")
    op.drop_column("freelancer_profiles", "current_level_id")
    op.add_column(
        "freelancer_profiles",
        sa.Column("current_level", sa.String(length=20), nullable=True),
    )
    op.create_index(
        "ix_freelancer_profiles_current_level", "freelancer_profiles", ["current_level"], unique=False
    )

    # freelancer_level_history: old_level_id / new_level_id -> old_level / new_level enum strings
    op.drop_constraint(
        "fk_freelancer_level_history_old_level_id_freelancer_levels",
        "freelancer_level_history",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_freelancer_level_history_new_level_id_freelancer_levels",
        "freelancer_level_history",
        type_="foreignkey",
    )
    op.drop_index("ix_freelancer_level_history_new_level_id", table_name="freelancer_level_history")
    op.drop_column("freelancer_level_history", "old_level_id")
    op.drop_column("freelancer_level_history", "new_level_id")
    op.add_column(
        "freelancer_level_history",
        sa.Column("old_level", sa.String(length=20), nullable=True),
    )
    op.add_column(
        "freelancer_level_history",
        sa.Column("new_level", sa.String(length=20), nullable=False),
    )
    op.create_index(
        "ix_freelancer_level_history_new_level", "freelancer_level_history", ["new_level"], unique=False
    )

    # drop the now-unreferenced freelancer_levels table
    op.drop_index("ix_freelancer_levels_level_key", table_name="freelancer_levels")
    op.drop_table("freelancer_levels")

    # projects: introduce required_level for eligibility filtering
    op.add_column(
        "projects",
        sa.Column("required_level", sa.String(length=20), nullable=True),
    )
    op.create_index("ix_projects_required_level", "projects", ["required_level"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_projects_required_level", table_name="projects")
    op.drop_column("projects", "required_level")

    op.create_table(
        "freelancer_levels",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("level_key", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("rank_order", sa.Integer(), nullable=False),
        sa.Column("access_type", sa.String(length=20), nullable=False),
        sa.Column("min_completed_projects", sa.Integer(), nullable=False),
        sa.Column("min_rating", sa.Numeric(precision=3, scale=2), nullable=True),
        sa.Column("max_active_applications", sa.Integer(), nullable=True),
        sa.Column("can_apply_public_projects", sa.Boolean(), nullable=False),
        sa.Column("can_apply_private_projects", sa.Boolean(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_freelancer_levels")),
    )
    op.create_index(op.f("ix_freelancer_levels_level_key"), "freelancer_levels", ["level_key"], unique=True)

    op.drop_index("ix_freelancer_level_history_new_level", table_name="freelancer_level_history")
    op.drop_column("freelancer_level_history", "new_level")
    op.drop_column("freelancer_level_history", "old_level")
    op.add_column(
        "freelancer_level_history",
        sa.Column("new_level_id", sa.String(length=36), nullable=False),
    )
    op.add_column(
        "freelancer_level_history",
        sa.Column("old_level_id", sa.String(length=36), nullable=True),
    )
    op.create_index(
        "ix_freelancer_level_history_new_level_id", "freelancer_level_history", ["new_level_id"], unique=False
    )
    op.create_foreign_key(
        "fk_freelancer_level_history_new_level_id_freelancer_levels",
        "freelancer_level_history",
        "freelancer_levels",
        ["new_level_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_freelancer_level_history_old_level_id_freelancer_levels",
        "freelancer_level_history",
        "freelancer_levels",
        ["old_level_id"],
        ["id"],
    )

    op.drop_index("ix_freelancer_profiles_current_level", table_name="freelancer_profiles")
    op.drop_column("freelancer_profiles", "current_level")
    op.add_column(
        "freelancer_profiles",
        sa.Column("current_level_id", sa.String(length=36), nullable=True),
    )
    op.create_index(
        "ix_freelancer_profiles_current_level_id", "freelancer_profiles", ["current_level_id"], unique=False
    )
    op.create_foreign_key(
        "fk_freelancer_profiles_current_level_id_freelancer_levels",
        "freelancer_profiles",
        "freelancer_levels",
        ["current_level_id"],
        ["id"],
    )