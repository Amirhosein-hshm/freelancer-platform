from typing import Any

from sqlalchemy import func, or_, select, union_all
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.domain.project.enums import ProjectStatus
from app.domain.shared.types import EntityId
from app.domain.ticketing.read_models import RelatedUser
from app.domain.ticketing.repositories import IRelatedUsersRepository
from app.infrastructure.db.models.category_models import CategorySupervisorModel
from app.infrastructure.db.models.freelancer_models import FreelancerProfileModel
from app.infrastructure.db.models.iam_models import UserModel
from app.infrastructure.db.models.project_models import (
    ProjectApplicationModel,
    ProjectModel,
)

_OPEN_STATUSES = (
    ProjectStatus.PUBLISHED.value,
    ProjectStatus.COLLECTING_APPLICATIONS.value,
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

    async def list_related_users(self, user_id: EntityId, limit: int, offset: int) -> list[RelatedUser]:
        ids = self._related_user_ids_subquery(user_id)
        result = await self._session.execute(
            select(
                UserModel.id,
                UserModel.email,
                UserModel.first_name,
                UserModel.last_name,
            )
            .join(ids, ids.c.related_user_id == UserModel.id)
            .where(UserModel.deleted_at.is_(None))
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

    async def count_related_users(self, user_id: EntityId) -> int:
        ids = self._related_user_ids_subquery(user_id)
        result = await self._session.execute(
            select(func.count())
            .select_from(ids)
            .join(UserModel, UserModel.id == ids.c.related_user_id)
            .where(UserModel.deleted_at.is_(None))
        )
        return int(result.scalar_one())

    def _related_user_ids_subquery(self, user_id: EntityId) -> Any:
        application = ProjectApplicationModel
        profile = FreelancerProfileModel
        project = ProjectModel
        cs1 = aliased(CategorySupervisorModel)
        cs2 = aliased(CategorySupervisorModel)

        _selected_freelancer_condition = project.deleted_at.is_(None)
        _selected_freelancer_join = (
            select(profile.user_id.label("related_user_id"))
            .select_from(project)
            .join(application, application.id == project.selected_application_id)
            .join(profile, profile.id == application.freelancer_profile_id)
        )

        parts: list[Any] = [
            # --- Project anchor: user as customer ---
            select(project.assigned_supervisor_user_id.label("related_user_id")).where(
                project.customer_user_id == user_id,
                project.assigned_supervisor_user_id.is_not(None),
                project.deleted_at.is_(None),
            ),
            _selected_freelancer_join.where(
                project.customer_user_id == user_id,
                _selected_freelancer_condition,
            ),
            # --- Project anchor: user as assigned supervisor ---
            select(project.customer_user_id.label("related_user_id")).where(
                project.assigned_supervisor_user_id == user_id,
                project.deleted_at.is_(None),
            ),
            _selected_freelancer_join.where(
                project.assigned_supervisor_user_id == user_id,
                _selected_freelancer_condition,
            ),
            # --- Project anchor: user as selected freelancer ---
            select(project.customer_user_id.label("related_user_id"))
            .select_from(project)
            .join(application, application.id == project.selected_application_id)
            .join(profile, profile.id == application.freelancer_profile_id)
            .where(profile.user_id == user_id, project.deleted_at.is_(None)),
            select(project.assigned_supervisor_user_id.label("related_user_id"))
            .select_from(project)
            .join(application, application.id == project.selected_application_id)
            .join(profile, profile.id == application.freelancer_profile_id)
            .where(
                profile.user_id == user_id,
                project.assigned_supervisor_user_id.is_not(None),
                project.deleted_at.is_(None),
            ),
            # --- Category anchor: co-supervisors of categories the user supervises ---
            select(cs2.supervisor_user_id.label("related_user_id"))
            .select_from(cs1)
            .join(cs2, cs2.category_id == cs1.category_id)
            .where(
                cs1.supervisor_user_id == user_id,
                cs1.is_active.is_(True),
                cs2.is_active.is_(True),
                cs2.supervisor_user_id != user_id,
            ),
            # --- Category anchor: customers of open projects in supervised categories ---
            select(project.customer_user_id.label("related_user_id"))
            .select_from(CategorySupervisorModel)
            .join(project, project.category_id == CategorySupervisorModel.category_id)
            .where(
                CategorySupervisorModel.supervisor_user_id == user_id,
                CategorySupervisorModel.is_active.is_(True),
                project.status.in_(_OPEN_STATUSES),
                project.deleted_at.is_(None),
            ),
            # --- Category anchor: selected freelancers of open projects in supervised categories ---
            select(profile.user_id.label("related_user_id"))
            .select_from(CategorySupervisorModel)
            .join(project, project.category_id == CategorySupervisorModel.category_id)
            .join(application, application.id == project.selected_application_id)
            .join(profile, profile.id == application.freelancer_profile_id)
            .where(
                CategorySupervisorModel.supervisor_user_id == user_id,
                CategorySupervisorModel.is_active.is_(True),
                project.status.in_(_OPEN_STATUSES),
                project.deleted_at.is_(None),
            ),
            # --- Category anchor: active supervisors of categories where the user has an open project ---
            select(CategorySupervisorModel.supervisor_user_id.label("related_user_id"))
            .select_from(project)
            .join(
                CategorySupervisorModel,
                CategorySupervisorModel.category_id == project.category_id,
            )
            .where(
                CategorySupervisorModel.is_active.is_(True),
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