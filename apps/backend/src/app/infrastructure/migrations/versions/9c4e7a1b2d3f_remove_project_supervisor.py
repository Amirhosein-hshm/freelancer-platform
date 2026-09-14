"""Remove obsolete project-level supervisor assignment."""

import sqlalchemy as sa
from alembic import op

revision = "9c4e7a1b2d3f"
down_revision = "b4d2e6f8a901"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_index("ix_projects_assigned_supervisor_user_id", table_name="projects")
    op.drop_constraint("fk_projects_assigned_supervisor_user_id_users", "projects", type_="foreignkey")
    op.drop_column("projects", "assigned_supervisor_user_id")
    op.create_index(
        "uq_category_supervisors_active_pair",
        "category_supervisors",
        ["category_id", "supervisor_user_id"],
        unique=True,
        postgresql_where=sa.column("is_active").is_(True),
    )
    op.create_index(
        "uq_category_supervisors_active_primary",
        "category_supervisors",
        ["category_id"],
        unique=True,
        postgresql_where=sa.and_(
            sa.column("is_active").is_(True),
            sa.column("is_primary").is_(True),
        ),
    )


def downgrade() -> None:
    op.drop_index("uq_category_supervisors_active_primary", table_name="category_supervisors")
    op.drop_index("uq_category_supervisors_active_pair", table_name="category_supervisors")
    op.add_column("projects", sa.Column("assigned_supervisor_user_id", sa.String(length=36), nullable=True))
    op.create_foreign_key(
        "fk_projects_assigned_supervisor_user_id_users", "projects", "users", ["assigned_supervisor_user_id"], ["id"]
    )
    op.create_index("ix_projects_assigned_supervisor_user_id", "projects", ["assigned_supervisor_user_id"], unique=False)
