from app.application.shared.authorization import IAuthorizationService
from app.application.shared.ports import IFileAccessPolicy, IFileStorageService
from app.domain.freelancer.repositories import (
    IFreelancerProfileRepository,
    IPortfolioItemRepository,
    IResumeRepository,
)
from app.domain.project.repositories import (
    IProjectApplicationRepository,
    IProjectDeliveryRepository,
    IProjectRepository,
)
from app.domain.shared.types import EntityId
from app.domain.ticketing.repositories import (
    ITicketMessageRepository,
    ITicketParticipantRepository,
    ITicketRepository,
)


class DomainFileAccessPolicy(IFileAccessPolicy):
    """Context-aware file access using domain repositories.

    Access is granted when any of the following is true:

    - The actor is the uploader/owner of the file asset.
    - The actor has the ``file.read_any`` permission (admin override).
    - The file is referenced by the actor's own resume or portfolio item.
    - The file is referenced by a project delivery and the actor is the project
      customer, the selected freelancer, or the assigned supervisor.
    - The file is referenced by a ticket message and the actor is a current
      participant of that ticket (including the requester and assignee).
    """

    def __init__(
        self,
        file_storage: IFileStorageService,
        authorization_service: IAuthorizationService,
        profile_repo: IFreelancerProfileRepository,
        resume_repo: IResumeRepository,
        portfolio_item_repo: IPortfolioItemRepository,
        project_repo: IProjectRepository,
        project_application_repo: IProjectApplicationRepository,
        project_delivery_repo: IProjectDeliveryRepository,
        ticket_repo: ITicketRepository,
        ticket_participant_repo: ITicketParticipantRepository,
        ticket_message_repo: ITicketMessageRepository,
    ) -> None:
        self._file_storage = file_storage
        self._authorization_service = authorization_service
        self._profile_repo = profile_repo
        self._resume_repo = resume_repo
        self._portfolio_item_repo = portfolio_item_repo
        self._project_repo = project_repo
        self._project_application_repo = project_application_repo
        self._project_delivery_repo = project_delivery_repo
        self._ticket_repo = ticket_repo
        self._ticket_participant_repo = ticket_participant_repo
        self._ticket_message_repo = ticket_message_repo

    async def can_access(self, actor_id: EntityId, file_asset_id: EntityId) -> bool:
        try:
            metadata = await self._file_storage.get_metadata(file_asset_id)
        except (KeyError, FileNotFoundError):
            return False

        if metadata.owner_user_id == actor_id:
            return True

        if await self._authorization_service.has_permission(actor_id, "file.read_any"):
            return True

        if await self._is_resume_or_portfolio_owner(actor_id, file_asset_id):
            return True

        if await self._is_project_stakeholder(actor_id, file_asset_id):
            return True

        return await self._is_ticket_participant(actor_id, file_asset_id)

    async def _is_resume_or_portfolio_owner(self, actor_id: EntityId, file_asset_id: EntityId) -> bool:
        try:
            resume = await self._resume_repo.get_by_file_asset_id(file_asset_id)
        except Exception:
            resume = None
        if resume is not None:
            profile = await self._profile_repo.get_by_id(resume.freelancer_profile_id)
            return profile.user_id == actor_id

        try:
            item = await self._portfolio_item_repo.get_by_file_asset_id(file_asset_id)
        except Exception:
            item = None
        if item is not None:
            profile = await self._profile_repo.get_by_id(item.freelancer_profile_id)
            return profile.user_id == actor_id

        return False

    async def _is_project_stakeholder(self, actor_id: EntityId, file_asset_id: EntityId) -> bool:
        deliveries = await self._project_delivery_repo.list_by_file_asset_id(file_asset_id)
        for delivery in deliveries:
            project = await self._project_repo.get_by_id(delivery.project_id)
            if project.customer_user_id == actor_id:
                return True
            if project.assigned_supervisor_user_id == actor_id:
                return True
            if project.selected_application_id is not None:
                try:
                    application = await self._project_application_repo.get_by_id(project.selected_application_id)
                    profile = await self._profile_repo.get_by_id(application.freelancer_profile_id)
                    if profile.user_id == actor_id:
                        return True
                except Exception:
                    pass
        return False

    async def _is_ticket_participant(self, actor_id: EntityId, file_asset_id: EntityId) -> bool:
        messages = await self._ticket_message_repo.list_by_file_asset_id(file_asset_id)
        for message in messages:
            ticket = await self._ticket_repo.get_by_id(message.ticket_id)
            if ticket.created_by_user_id == actor_id:
                return True
            if ticket.assigned_to_user_id == actor_id:
                return True
            if await self._ticket_participant_repo.is_participant(ticket.id, actor_id):
                return True
        return False
