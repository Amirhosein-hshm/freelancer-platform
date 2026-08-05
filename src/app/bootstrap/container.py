from fastapi import Depends, FastAPI

from app.infrastructure.clock import SystemClock
from app.infrastructure.code_generators import (
    SqlSequenceProjectCodeGenerator,
    SqlSequenceTicketCodeGenerator,
)
from app.infrastructure.config import get_settings
from app.infrastructure.db.session import get_db_session
from app.infrastructure.db.unit_of_work import SqlAlchemyUnitOfWork
from app.infrastructure.id_generator import UuidIdGenerator
from app.infrastructure.notifications.websocket_notification_service import (
    WebSocketNotificationService,
)
from app.infrastructure.repositories.category_repository import SqlAlchemyCategoryRepository
from app.infrastructure.repositories.category_supervisor_repository import (
    SqlAlchemyCategorySupervisorRepository,
)
from app.infrastructure.repositories.customer_review_repository import (
    SqlAlchemyCustomerReviewRepository,
)
from app.infrastructure.repositories.form_template_repository import (
    SqlAlchemyFormTemplateRepository,
)
from app.infrastructure.repositories.freelancer_level_history_repository import (
    SqlAlchemyFreelancerLevelHistoryRepository,
)
from app.infrastructure.repositories.freelancer_level_repository import (
    SqlAlchemyFreelancerLevelRepository,
)
from app.infrastructure.repositories.freelancer_profile_repository import (
    SqlAlchemyFreelancerProfileRepository,
)
from app.infrastructure.repositories.permission_repository import (
    SqlAlchemyPermissionRepository,
)
from app.infrastructure.repositories.portfolio_item_repository import (
    SqlAlchemyPortfolioItemRepository,
)
from app.infrastructure.repositories.project_application_repository import (
    SqlAlchemyProjectApplicationRepository,
)
from app.infrastructure.repositories.project_delivery_repository import (
    SqlAlchemyProjectDeliveryRepository,
)
from app.infrastructure.repositories.project_repository import SqlAlchemyProjectRepository
from app.infrastructure.repositories.project_revision_request_repository import (
    SqlAlchemyProjectRevisionRequestRepository,
)
from app.infrastructure.repositories.project_status_history_repository import (
    SqlAlchemyProjectStatusHistoryRepository,
)
from app.infrastructure.repositories.rating_repository import SqlAlchemyRatingRepository
from app.infrastructure.repositories.refresh_token_repository import (
    SqlAlchemyRefreshTokenRepository,
)
from app.infrastructure.repositories.reporting_read_repository import (
    SqlAlchemyReportingReadRepository,
)
from app.infrastructure.repositories.resume_repository import SqlAlchemyResumeRepository
from app.infrastructure.repositories.role_permission_repository import (
    SqlAlchemyRolePermissionRepository,
)
from app.infrastructure.repositories.role_repository import SqlAlchemyRoleRepository
from app.infrastructure.repositories.supervisor_review_repository import (
    SqlAlchemySupervisorReviewRepository,
)
from app.infrastructure.repositories.ticket_message_repository import (
    SqlAlchemyTicketMessageRepository,
)
from app.infrastructure.repositories.ticket_participant_repository import (
    SqlAlchemyTicketParticipantRepository,
)
from app.infrastructure.repositories.ticket_repository import SqlAlchemyTicketRepository
from app.infrastructure.repositories.user_repository import SqlAlchemyUserRepository
from app.infrastructure.repositories.user_role_repository import (
    SqlAlchemyUserRoleRepository,
)
from app.infrastructure.security.authorization_service import (
    SqlAlchemyAuthorizationService,
)
from app.infrastructure.security.password_hasher import Argon2PasswordHasher
from app.infrastructure.security.token_service import JwtTokenService
from app.infrastructure.storage.file_storage import InMemoryFileStorageService
from app.presentation.core import providers
from app.presentation.main import create_app


def build_app() -> FastAPI:
    app = create_app()
    settings = get_settings()

    password_hasher = Argon2PasswordHasher()
    id_generator = UuidIdGenerator()
    clock = SystemClock()
    token_service = JwtTokenService(
        secret=settings.jwt_secret,
        access_ttl_minutes=settings.jwt_access_ttl_minutes,
        refresh_ttl_days=settings.jwt_refresh_ttl_days,
    )
    notification_service = WebSocketNotificationService()
    file_storage_service = InMemoryFileStorageService()

    app.dependency_overrides[providers.get_password_hasher] = lambda: password_hasher
    app.dependency_overrides[providers.get_id_generator] = lambda: id_generator
    app.dependency_overrides[providers.get_clock] = lambda: clock
    app.dependency_overrides[providers.get_token_service] = lambda: token_service
    app.dependency_overrides[providers.get_notification_service] = lambda: notification_service
    app.dependency_overrides[providers.get_file_storage_service] = lambda: file_storage_service

    app.dependency_overrides[providers.get_unit_of_work] = (
        lambda session=Depends(get_db_session): SqlAlchemyUnitOfWork(session)
    )
    app.dependency_overrides[providers.get_authorization_service] = (
        lambda session=Depends(get_db_session): SqlAlchemyAuthorizationService(session)
    )
    app.dependency_overrides[providers.get_project_code_generator] = (
        lambda session=Depends(get_db_session): SqlSequenceProjectCodeGenerator(session)
    )
    app.dependency_overrides[providers.get_ticket_code_generator] = (
        lambda session=Depends(get_db_session): SqlSequenceTicketCodeGenerator(session)
    )

    app.dependency_overrides[providers.get_user_repository] = (
        lambda session=Depends(get_db_session): SqlAlchemyUserRepository(session)
    )
    app.dependency_overrides[providers.get_role_repository] = (
        lambda session=Depends(get_db_session): SqlAlchemyRoleRepository(session)
    )
    app.dependency_overrides[providers.get_permission_repository] = (
        lambda session=Depends(get_db_session): SqlAlchemyPermissionRepository(session)
    )
    app.dependency_overrides[providers.get_user_role_repository] = (
        lambda session=Depends(get_db_session): SqlAlchemyUserRoleRepository(session)
    )
    app.dependency_overrides[providers.get_role_permission_repository] = (
        lambda session=Depends(get_db_session): SqlAlchemyRolePermissionRepository(session)
    )
    app.dependency_overrides[providers.get_refresh_token_repository] = (
        lambda session=Depends(get_db_session): SqlAlchemyRefreshTokenRepository(session)
    )
    app.dependency_overrides[providers.get_category_repository] = (
        lambda session=Depends(get_db_session): SqlAlchemyCategoryRepository(session)
    )
    app.dependency_overrides[providers.get_category_supervisor_repository] = (
        lambda session=Depends(get_db_session): SqlAlchemyCategorySupervisorRepository(session)
    )
    app.dependency_overrides[providers.get_freelancer_profile_repository] = (
        lambda session=Depends(get_db_session): SqlAlchemyFreelancerProfileRepository(session)
    )
    app.dependency_overrides[providers.get_freelancer_level_repository] = (
        lambda session=Depends(get_db_session): SqlAlchemyFreelancerLevelRepository(session)
    )
    app.dependency_overrides[providers.get_freelancer_level_history_repository] = (
        lambda session=Depends(get_db_session): SqlAlchemyFreelancerLevelHistoryRepository(session)
    )
    app.dependency_overrides[providers.get_resume_repository] = (
        lambda session=Depends(get_db_session): SqlAlchemyResumeRepository(session)
    )
    app.dependency_overrides[providers.get_portfolio_item_repository] = (
        lambda session=Depends(get_db_session): SqlAlchemyPortfolioItemRepository(session)
    )
    app.dependency_overrides[providers.get_form_template_repository] = (
        lambda session=Depends(get_db_session): SqlAlchemyFormTemplateRepository(session)
    )
    app.dependency_overrides[providers.get_project_repository] = (
        lambda session=Depends(get_db_session): SqlAlchemyProjectRepository(session)
    )
    app.dependency_overrides[providers.get_project_application_repository] = (
        lambda session=Depends(get_db_session): SqlAlchemyProjectApplicationRepository(session)
    )
    app.dependency_overrides[providers.get_project_delivery_repository] = (
        lambda session=Depends(get_db_session): SqlAlchemyProjectDeliveryRepository(session)
    )
    app.dependency_overrides[providers.get_project_revision_request_repository] = (
        lambda session=Depends(get_db_session): SqlAlchemyProjectRevisionRequestRepository(session)
    )
    app.dependency_overrides[providers.get_project_status_history_repository] = (
        lambda session=Depends(get_db_session): SqlAlchemyProjectStatusHistoryRepository(session)
    )
    app.dependency_overrides[providers.get_customer_review_repository] = (
        lambda session=Depends(get_db_session): SqlAlchemyCustomerReviewRepository(session)
    )
    app.dependency_overrides[providers.get_supervisor_review_repository] = (
        lambda session=Depends(get_db_session): SqlAlchemySupervisorReviewRepository(session)
    )
    app.dependency_overrides[providers.get_rating_repository] = (
        lambda session=Depends(get_db_session): SqlAlchemyRatingRepository(session)
    )
    app.dependency_overrides[providers.get_ticket_repository] = (
        lambda session=Depends(get_db_session): SqlAlchemyTicketRepository(session)
    )
    app.dependency_overrides[providers.get_ticket_message_repository] = (
        lambda session=Depends(get_db_session): SqlAlchemyTicketMessageRepository(session)
    )
    app.dependency_overrides[providers.get_ticket_participant_repository] = (
        lambda session=Depends(get_db_session): SqlAlchemyTicketParticipantRepository(session)
    )
    app.dependency_overrides[providers.get_reporting_read_repository] = (
        lambda session=Depends(get_db_session): SqlAlchemyReportingReadRepository(session)
    )

    return app