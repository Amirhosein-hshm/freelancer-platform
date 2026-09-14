from typing import Any

import sqlalchemy as sa
from sqlalchemy import func, or_, select, union_all
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.domain.project.enums import ProjectStatus
from app.domain.shared.types import EntityId
from app.domain.ticketing.read_models import RelatedUser
from app.domain.ticketing.repositories import IRelatedUsersRepository
from app.infrastructure.db.models.category_models import CategoryModel, CategorySupervisorModel
from app.infrastructure.db.models.freelancer_models import FreelancerProfileModel
from app.infrastructure.db.models.iam_models import RoleModel, UserModel, UserRoleModel
from app.infrastructure.db.models.project_models import (
    ProjectApplicationModel,
    ProjectModel,
)

_OPEN_STATUSES = (
    ProjectStatus.PUBLISHED.value,
    ProjectStatus.COLLECTING_APPLICATIONS.value,
)
_NON_TERMINAL_STATUSES = tuple(
    status.value for status in ProjectStatus if status not in (ProjectStatus.COMPLETED, ProjectStatus.CANCELLED)
)


class SqlAlchemyRelatedUsersRepository(IRelatedUsersRepository):
    """Enumerate users related to ``user_id`` per the two-party ticket rules.

    Relationships come from two anchors (mirroring ``RelationshipEligibilityService``):

    - **Project**: stakeholders (customer, assigned supervisor, selected freelancer)
      of any non-deleted project the user is a stakeholder of.
    - **Category**: active supervisors of categories the user supervises, plus active
      supervisors of categories where the user has an open project (as customer or
      selected freelancer); also the customers/selected freelancers of open projects
      in categories the user supervises, plus co-supervisors.

    Project-anchored links use any project status; category-anchored links only count
    open projects (``published``/``collecting_applications``), matching the service.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def are_related(self, user_a: EntityId, user_b: EntityId) -> bool:
        rows = await self.list_related_users(user_a, limit=10000, offset=0)
        return any(row.user_id == user_b for row in rows)

    def _filtered_users_stmt(self, user_id: EntityId, search: str | None, role: str | None):
        ids = self._related_user_ids_subquery(user_id)
        stmt = (
            select(UserModel.id, UserModel.email, UserModel.first_name, UserModel.last_name)
            .join(ids, ids.c.related_user_id == UserModel.id)
            .where(UserModel.deleted_at.is_(None))
        )
        if search and (term := search.strip()):
            pattern = f"%{term}%"
            stmt = stmt.where(
                or_(
                    UserModel.email.ilike(pattern),
                    UserModel.first_name.ilike(pattern),
                    UserModel.last_name.ilike(pattern),
                )
            )
        if role:
            stmt = stmt.where(
                select(UserRoleModel.id)
                .join(RoleModel, RoleModel.id == UserRoleModel.role_id)
                .where(
                    UserRoleModel.user_id == UserModel.id,
                    UserRoleModel.is_active.is_(True),
                    UserRoleModel.revoked_at.is_(None),
                    RoleModel.role_key == role,
                )
                .exists()
            )
        return stmt

    async def list_related_users(
        self,
        user_id: EntityId,
        limit: int,
        offset: int,
        search: str | None = None,
        role: str | None = None,
    ) -> list[RelatedUser]:
        result = await self._session.execute(
            self._filtered_users_stmt(user_id, search, role)
            .order_by(UserModel.created_at.desc(), UserModel.id)
            .limit(limit)
            .offset(offset)
        )
        return [
            RelatedUser(
                user_id=row.id,
                email=row.email,
                first_name=row.first_name,
                last_name=row.last_name,
            )
            for row in result
        ]

    async def count_related_users(
        self,
        user_id: EntityId,
        search: str | None = None,
        role: str | None = None,
    ) -> int:
        result = await self._session.execute(
            select(func.count()).select_from(self._filtered_users_stmt(user_id, search, role).subquery())
        )
        return int(result.scalar_one())

    def _related_user_ids_subquery(self, user_id: EntityId) -> Any:
        application = ProjectApplicationModel
        profile = FreelancerProfileModel
        project = ProjectModel
        cs1 = aliased(CategorySupervisorModel)
        cs2 = aliased(CategorySupervisorModel)

        ancestors = select(
            CategoryModel.id.label("project_category_id"),
            CategoryModel.id.label("ancestor_category_id"),
            sa.literal(0).label("depth"),
        ).where(CategoryModel.deleted_at.is_(None)).cte("related_category_ancestors", recursive=True)
        current = CategoryModel.__table__.alias("related_current")
        parent = CategoryModel.__table__.alias("related_parent")
        ancestors = ancestors.union_all(
            select(ancestors.c.project_category_id, parent.c.id, ancestors.c.depth + 1)
            .select_from(
                ancestors.join(current, current.c.id == ancestors.c.ancestor_category_id).join(
                    parent, parent.c.id == current.c.parent_category_id
                )
            )
            .where(parent.c.deleted_at.is_(None))
        )
        effective = (
            select(
                ancestors.c.project_category_id,
                CategorySupervisorModel.supervisor_user_id,
                func.row_number()
                .over(
                    partition_by=ancestors.c.project_category_id,
                    order_by=(
                        ancestors.c.depth,
                        CategorySupervisorModel.is_primary.desc(),
                        CategorySupervisorModel.id,
                    ),
                )
                .label("rn"),
            )
            .join(CategorySupervisorModel, CategorySupervisorModel.category_id == ancestors.c.ancestor_category_id)
            .join(UserModel, UserModel.id == CategorySupervisorModel.supervisor_user_id)
            .where(
                CategorySupervisorModel.is_active.is_(True),
                UserModel.deleted_at.is_(None),
                UserModel.status == "active",
            )
            .subquery("related_effective_supervisors")
        )

        _selected_freelancer_condition = (
            project.deleted_at.is_(None) & project.status.in_(_NON_TERMINAL_STATUSES)
        )
        _selected_freelancer_join = (
            select(profile.user_id.label("related_user_id"))
            .select_from(project)
            .join(application, application.id == project.selected_application_id)
            .join(profile, profile.id == application.freelancer_profile_id)
        )

        parts: list[Any] = [
            # Admins may message any other active user.
            select(UserModel.id.label("related_user_id"))
            .select_from(UserModel)
            .join(UserRoleModel, UserRoleModel.user_id == UserModel.id)
            .join(RoleModel, RoleModel.id == UserRoleModel.role_id)
            .where(
                RoleModel.role_key == "admin",
                UserRoleModel.is_active.is_(True),
                UserRoleModel.revoked_at.is_(None),
                UserModel.deleted_at.is_(None),
                UserModel.id != user_id,
            ),
            # An admin can target every other active user.
            select(UserModel.id.label("related_user_id")).where(
                UserModel.deleted_at.is_(None), UserModel.id != user_id
            ).where(
                select(UserRoleModel.id)
                .join(RoleModel, RoleModel.id == UserRoleModel.role_id)
                .where(
                    UserRoleModel.user_id == user_id,
                    UserRoleModel.is_active.is_(True),
                    UserRoleModel.revoked_at.is_(None),
                    RoleModel.role_key == "admin",
                )
                .exists()
            ),
            _selected_freelancer_join.where(
                project.customer_user_id == user_id,
                _selected_freelancer_condition,
            ),
            # --- Project anchor: user as selected freelancer ---
            select(project.customer_user_id.label("related_user_id"))
            .select_from(project)
            .join(application, application.id == project.selected_application_id)
            .join(profile, profile.id == application.freelancer_profile_id)
            .where(
                profile.user_id == user_id,
                project.deleted_at.is_(None),
                project.status.in_(_NON_TERMINAL_STATUSES),
            ),
            # --- Category anchor: co-supervisors of categories the user supervises ---
            select(cs2.supervisor_user_id.label("related_user_id"))
            .select_from(cs1)
            .join(cs2, cs2.category_id == cs1.category_id)
            .where(
                cs1.is_active.is_(True),
                cs2.is_active.is_(True),
                cs2.supervisor_user_id != user_id,
            ),
            # --- Category anchor: customers of non-terminal projects in supervised categories ---
            select(project.customer_user_id.label("related_user_id"))
            .select_from(project)
            .join(effective, effective.c.project_category_id == project.category_id)
            .where(
                effective.c.rn == 1,
                effective.c.supervisor_user_id == user_id,
                project.status.in_(_NON_TERMINAL_STATUSES),
                project.deleted_at.is_(None),
            ),
            # --- Category anchor: selected freelancers of non-terminal projects in supervised categories ---
            select(profile.user_id.label("related_user_id"))
            .select_from(project)
            .join(effective, effective.c.project_category_id == project.category_id)
            .join(application, application.id == project.selected_application_id)
            .join(profile, profile.id == application.freelancer_profile_id)
            .where(
                effective.c.rn == 1,
                effective.c.supervisor_user_id == user_id,
                project.status.in_(_NON_TERMINAL_STATUSES),
                project.deleted_at.is_(None),
            ),
            # --- Category anchor: active supervisors of categories where the user has an open project ---
            select(effective.c.supervisor_user_id.label("related_user_id"))
            .select_from(project)
            .join(effective, effective.c.project_category_id == project.category_id)
            .where(
                effective.c.rn == 1,
                project.status.in_(_OPEN_STATUSES),
                project.deleted_at.is_(None),
                or_(
                    project.customer_user_id == user_id,
                    project.selected_application_id.in_(
                        select(application.id)
                        .join(profile, profile.id == application.freelancer_profile_id)
                        .where(profile.user_id == user_id)
                    ),
                ),
            ),
        ]

        related = union_all(*parts).subquery()
        return (
            select(related.c.related_user_id)
            .distinct()
            .where(
                related.c.related_user_id.is_not(None),
                related.c.related_user_id != user_id,
            )
            .subquery()
        )
