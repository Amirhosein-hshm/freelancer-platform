"""Presentation-layer test fixtures.

Per TESTING.md §9 these tests use FastAPI's ``TestClient`` with
``app.dependency_overrides`` pointed at the same async Fakes used by the
application tests — never a real database. The app is built from
``create_app()`` (no infrastructure wiring), then every leaf provider stub in
``presentation/core/providers.py`` is overridden with a fresh Fake so the real
use cases run against in-memory repositories.
"""

from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from app.presentation.core import providers
from app.presentation.main import create_app
from tests.fakes.fake_authorization_service import FakeAuthorizationService
from tests.fakes.fake_category_repository import FakeCategoryRepository
from tests.fakes.fake_category_supervisor_repository import FakeCategorySupervisorRepository
from tests.fakes.fake_clock import FakeClock
from tests.fakes.fake_customer_review_repository import FakeCustomerReviewRepository
from tests.fakes.fake_file_storage import FakeFileStorageService
from tests.fakes.fake_form_template_repository import FakeFormTemplateRepository
from tests.fakes.fake_freelancer_level_history_repository import (
    FakeFreelancerLevelHistoryRepository,
)
from tests.fakes.fake_freelancer_level_repository import FakeFreelancerLevelRepository
from tests.fakes.fake_freelancer_profile_repository import FakeFreelancerProfileRepository
from tests.fakes.fake_id_generator import FakeIdGenerator
from tests.fakes.fake_notification_service import FakeNotificationService
from tests.fakes.fake_password_hasher import FakePasswordHasher
from tests.fakes.fake_permission_repository import FakePermissionRepository
from tests.fakes.fake_portfolio_item_repository import FakePortfolioItemRepository
from tests.fakes.fake_project_application_repository import FakeProjectApplicationRepository
from tests.fakes.fake_project_code_generator import FakeProjectCodeGenerator
from tests.fakes.fake_project_delivery_repository import FakeProjectDeliveryRepository
from tests.fakes.fake_project_repository import FakeProjectRepository
from tests.fakes.fake_project_revision_request_repository import (
    FakeProjectRevisionRequestRepository,
)
from tests.fakes.fake_project_status_history_repository import FakeProjectStatusHistoryRepository
from tests.fakes.fake_rating_repository import FakeRatingRepository
from tests.fakes.fake_refresh_token_repository import FakeRefreshTokenRepository
from tests.fakes.fake_reporting_read_repository import FakeReportingReadRepository
from tests.fakes.fake_resume_repository import FakeResumeRepository
from tests.fakes.fake_role_permission_repository import FakeRolePermissionRepository
from tests.fakes.fake_role_repository import FakeRoleRepository
from tests.fakes.fake_supervisor_review_repository import FakeSupervisorReviewRepository
from tests.fakes.fake_ticket_code_generator import FakeTicketCodeGenerator
from tests.fakes.fake_ticket_message_repository import FakeTicketMessageRepository
from tests.fakes.fake_ticket_participant_repository import FakeTicketParticipantRepository
from tests.fakes.fake_ticket_repository import FakeTicketRepository
from tests.fakes.fake_token_service import FakeTokenService
from tests.fakes.fake_unit_of_work import FakeUnitOfWork
from tests.fakes.fake_user_repository import FakeUserRepository
from tests.fakes.fake_user_role_repository import FakeUserRoleRepository

NOW = datetime(2026, 8, 2, tzinfo=UTC)

PASSWORD_HASHER = FakePasswordHasher()

def auth_header(_token_service: FakeTokenService, user_id: str, roles: list[str]) -> dict[str, str]:
    """Build an Authorization header matching FakeTokenService's token format.

    ``FakeTokenService.decode_access_token`` splits on ``.`` and expects
    ``access.<user_id>.<roles>`` where roles are comma-joined.
    """
    roles_part = ",".join(roles)
    token = f"access.{user_id}.{roles_part}"
    return {"Authorization": f"Bearer {token}"}


def _make_overrides() -> dict[object, object]:
    """Wire every leaf provider stub to a fresh fake instance."""
    role_repo = FakeRoleRepository()
    permission_repo = FakePermissionRepository()
    user_role_repo = FakeUserRoleRepository(role_repo)
    role_permission_repo = FakeRolePermissionRepository(permission_repo)

    overrides: dict[object, object] = {
        providers.get_authorization_service: FakeAuthorizationService(),
        providers.get_category_repository: FakeCategoryRepository(),
        providers.get_category_supervisor_repository: FakeCategorySupervisorRepository(),
        providers.get_clock: FakeClock(fixed_now=NOW),
        providers.get_customer_review_repository: FakeCustomerReviewRepository(),
        providers.get_file_storage_service: FakeFileStorageService(),
        providers.get_form_template_repository: FakeFormTemplateRepository(),
        providers.get_freelancer_level_history_repository: FakeFreelancerLevelHistoryRepository(),
        providers.get_freelancer_level_repository: FakeFreelancerLevelRepository(),
        providers.get_freelancer_profile_repository: FakeFreelancerProfileRepository(),
        providers.get_id_generator: FakeIdGenerator(),
        providers.get_notification_service: FakeNotificationService(),
        providers.get_password_hasher: PASSWORD_HASHER,
        providers.get_permission_repository: permission_repo,
        providers.get_portfolio_item_repository: FakePortfolioItemRepository(),
        providers.get_project_application_repository: FakeProjectApplicationRepository(),
        providers.get_project_code_generator: FakeProjectCodeGenerator(),
        providers.get_project_delivery_repository: FakeProjectDeliveryRepository(),
        providers.get_project_repository: FakeProjectRepository(),
        providers.get_project_revision_request_repository: FakeProjectRevisionRequestRepository(),
        providers.get_project_status_history_repository: FakeProjectStatusHistoryRepository(),
        providers.get_rating_repository: FakeRatingRepository(),
        providers.get_refresh_token_repository: FakeRefreshTokenRepository(),
        providers.get_reporting_read_repository: FakeReportingReadRepository(),
        providers.get_resume_repository: FakeResumeRepository(),
        providers.get_role_permission_repository: role_permission_repo,
        providers.get_role_repository: role_repo,
        providers.get_supervisor_review_repository: FakeSupervisorReviewRepository(),
        providers.get_ticket_code_generator: FakeTicketCodeGenerator(),
        providers.get_ticket_message_repository: FakeTicketMessageRepository(),
        providers.get_ticket_participant_repository: FakeTicketParticipantRepository(),
        providers.get_ticket_repository: FakeTicketRepository(),
        providers.get_token_service: FakeTokenService(),
        providers.get_unit_of_work: FakeUnitOfWork(),
        providers.get_user_repository: FakeUserRepository(),
        providers.get_user_role_repository: user_role_repo,
    }
    return overrides


@pytest.fixture
def overrides() -> dict[object, object]:
    """Fresh fake wiring for one test."""
    return _make_overrides()


@pytest.fixture
def client(overrides: dict[object, object]) -> TestClient:
    app = create_app()
    app.dependency_overrides.update(
        {provider: (lambda fake=instance: fake) for provider, instance in overrides.items()}
    )
    with TestClient(app) as test_client:
        yield test_client