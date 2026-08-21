"""Domain services for the Ticketing context.

Tickets are strictly two-party conversations (creator + target). ``RelationshipEligibilityService``
decides whether two users may open a ticket with each other, anchoring on a project or a category.
"""
from app.domain.category.repositories import ICategorySupervisorRepository
from app.domain.freelancer.repositories import IFreelancerProfileRepository
from app.domain.project.repositories import (
    IProjectApplicationRepository,
    IProjectRepository,
)
from app.domain.shared.types import EntityId
from app.domain.ticketing.exceptions import TicketRelationshipError


class RelationshipEligibilityService:
    """Decide whether two users have an eligible business relationship to open a two-party ticket.

    Anchors:

    - **Project**: both users are stakeholders of the same project — the customer, the selected
      freelancer (via the profile behind ``selected_application_id``), or the assigned supervisor.
    - **Category** (only when no project anchor is given): at least one of the two users is an
      active supervisor of the category and the other has a project in that category (as customer
      or selected freelancer), or both are active supervisors of the category.

    If neither anchor is provided there is no verifiable relationship, so the ticket is rejected.
    """

    def __init__(
        self,
        project_repo: IProjectRepository,
        project_application_repo: IProjectApplicationRepository,
        profile_repo: IFreelancerProfileRepository,
        category_supervisor_repo: ICategorySupervisorRepository,
    ) -> None:
        self._project_repo = project_repo
        self._project_application_repo = project_application_repo
        self._profile_repo = profile_repo
        self._category_supervisor_repo = category_supervisor_repo

    async def ensure_related(
        self,
        *,
        user_a: EntityId,
        user_b: EntityId,
        related_project_id: EntityId | None,
        related_category_id: EntityId | None,
    ) -> None:
        if not await self.are_related(
            user_a=user_a,
            user_b=user_b,
            related_project_id=related_project_id,
            related_category_id=related_category_id,
        ):
            raise TicketRelationshipError(
                f"Users {user_a} and {user_b} have no eligible relationship to open a ticket."
            )

    async def are_related(
        self,
        *,
        user_a: EntityId,
        user_b: EntityId,
        related_project_id: EntityId | None,
        related_category_id: EntityId | None,
    ) -> bool:
        if user_a == user_b:
            return False
        if related_project_id is not None:
            return await self._share_project(user_a, user_b, related_project_id)
        if related_category_id is not None:
            return await self._share_category(user_a, user_b, related_category_id)
        return False

    async def _share_project(self, user_a: EntityId, user_b: EntityId, project_id: EntityId) -> bool:
        project = await self._project_repo.get_by_id(project_id)
        stakeholders = {project.customer_user_id}
        if project.assigned_supervisor_user_id is not None:
            stakeholders.add(project.assigned_supervisor_user_id)
        if project.selected_application_id is not None:
            application = await self._project_application_repo.get_by_id(project.selected_application_id)
            profile = await self._profile_repo.get_by_id(application.freelancer_profile_id)
            stakeholders.add(profile.user_id)
        return user_a in stakeholders and user_b in stakeholders

    async def _share_category(self, user_a: EntityId, user_b: EntityId, category_id: EntityId) -> bool:
        supervisors = {
            link.supervisor_user_id
            for link in await self._category_supervisor_repo.list_active_supervisors(category_id)
        }
        if user_a in supervisors and user_b in supervisors:
            return True
        projects = await self._project_repo.list_by_category(category_id)
        for project in projects:
            stakeholders = {project.customer_user_id}
            if project.selected_application_id is not None:
                application = await self._project_application_repo.get_by_id(project.selected_application_id)
                profile = await self._profile_repo.get_by_id(application.freelancer_profile_id)
                stakeholders.add(profile.user_id)
            if user_a in supervisors and user_b in stakeholders:
                return True
            if user_b in supervisors and user_a in stakeholders:
                return True
        return False