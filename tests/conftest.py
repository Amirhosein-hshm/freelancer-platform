from datetime import UTC, datetime

import pytest

from tests.fakes.fake_authorization_service import FakeAuthorizationService
from tests.fakes.fake_clock import FakeClock
from tests.fakes.fake_event_publisher import FakeEventPublisher
from tests.fakes.fake_id_generator import FakeIdGenerator
from tests.fakes.fake_notification_service import FakeNotificationService
from tests.fakes.fake_password_hasher import FakePasswordHasher
from tests.fakes.fake_project_code_generator import FakeProjectCodeGenerator
from tests.fakes.fake_token_service import FakeTokenService
from tests.fakes.fake_unit_of_work import FakeUnitOfWork


@pytest.fixture
def clock():
    return FakeClock(fixed_now=datetime(2026, 8, 2, tzinfo=UTC))


@pytest.fixture
def id_generator():
    return FakeIdGenerator(prefix="test")


@pytest.fixture
def uow():
    return FakeUnitOfWork()


@pytest.fixture
def password_hasher():
    return FakePasswordHasher()


@pytest.fixture
def token_service():
    return FakeTokenService()


@pytest.fixture
def authorization_service():
    return FakeAuthorizationService()


@pytest.fixture
def event_publisher():
    return FakeEventPublisher()


@pytest.fixture
def notification_service():
    return FakeNotificationService()


@pytest.fixture
def project_code_generator():
    return FakeProjectCodeGenerator()
