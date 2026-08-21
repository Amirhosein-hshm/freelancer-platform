"""Regression tests for the systemic soft-delete filtering pass (task §2).

Every entity with a ``deleted_at`` column must disappear from every read path once
soft-deleted. The one deliberate exception is documented on
``ITicketMessageRepository.get_by_id``/``IUserRepository.email_exists_including_deleted``.
"""

from datetime import UTC, datetime

import pytest

from app.domain.category.entities import Category
from app.domain.category.exceptions import CategoryNotFoundError
from app.domain.form.entities import FormTemplate
from app.domain.form.enums import FormTemplateStatus
from app.domain.form.exceptions import FormTemplateNotFoundError
from app.domain.freelancer.entities import FreelancerProfile, PortfolioItem
from app.domain.freelancer.enums import FreelancerApprovalStatus
from app.domain.freelancer.exceptions import (
    FreelancerProfileNotFoundError,
    PortfolioItemNotFoundError,
)
from app.domain.iam.entities import User, UserRole
from app.domain.iam.enums import UserStatus
from app.domain.iam.exceptions import UserNotFoundError
from app.domain.iam.value_objects import Email, PasswordHash
from app.domain.shared.exceptions import InvalidStateTransitionError
from app.domain.ticketing.entities import Ticket, TicketMessage
from app.domain.ticketing.enums import TicketMessageType, TicketPriority, TicketStatus
from app.domain.ticketing.exceptions import TicketNotFoundError
from tests.fakes.fake_category_repository import FakeCategoryRepository
from tests.fakes.fake_form_template_repository import FakeFormTemplateRepository
from tests.fakes.fake_freelancer_profile_repository import FakeFreelancerProfileRepository
from tests.fakes.fake_portfolio_item_repository import FakePortfolioItemRepository
from tests.fakes.fake_role_repository import FakeRoleRepository
from tests.fakes.fake_ticket_message_repository import FakeTicketMessageRepository
from tests.fakes.fake_ticket_repository import FakeTicketRepository
from tests.fakes.fake_user_repository import FakeUserRepository
from tests.fakes.fake_user_role_repository import FakeUserRoleRepository

NOW = datetime(2026, 8, 2, tzinfo=UTC)


def _user(user_id: str = "u1", email: str = "u1@example.com", deleted: bool = False) -> User:
    return User(
        id=user_id,
        email=Email(email),
        phone=None,
        password_hash=PasswordHash("hash"),
        first_name="Jane",
        last_name="Doe",
        status=UserStatus.ACTIVE,
        created_at=NOW,
        deleted_at=NOW if deleted else None,
    )


class TestUserSoftDeleteFiltering:
    async def test_soft_deleted_user_cannot_be_found_by_email(self):
        """Login resolves the account via get_by_email: a deleted user must not authenticate."""
        repo = FakeUserRepository()
        await repo.add(_user(deleted=True))

        with pytest.raises(UserNotFoundError):
            await repo.get_by_email(Email("u1@example.com"))

    async def test_soft_deleted_user_hidden_from_every_read_path(self):
        repo = FakeUserRepository()
        await repo.add(_user(deleted=True))

        with pytest.raises(UserNotFoundError):
            await repo.get_by_id("u1")
        assert await repo.find_by_id("u1") is None
        assert await repo.exists_by_email(Email("u1@example.com")) is False
        assert await repo.list_all(limit=10, offset=0) == []
        assert await repo.list_by_status(UserStatus.ACTIVE, limit=10, offset=0) == []
        assert await repo.count_all() == 0
        assert await repo.count_all(UserStatus.ACTIVE) == 0

    async def test_email_of_soft_deleted_user_stays_occupied(self):
        """Mirrors the users.email UNIQUE constraint so re-registration fails cleanly
        with DuplicateEmailError instead of a DB IntegrityError."""
        repo = FakeUserRepository()
        await repo.add(_user(deleted=True))

        assert await repo.email_exists_including_deleted(Email("u1@example.com")) is True
        assert await repo.exists_by_email(Email("u1@example.com")) is False

    async def test_live_user_still_visible(self):
        repo = FakeUserRepository()
        await repo.add(_user())

        assert (await repo.get_by_id("u1")).id == "u1"
        assert (await repo.get_by_email(Email("u1@example.com"))).id == "u1"
        assert await repo.count_all() == 1


class TestSoftDeletedAdminDoesNotCountAsAdmin:
    async def test_deleted_admin_excluded_from_active_role_holders(self):
        """A soft-deleted admin must not satisfy the last-admin guards."""
        user_repo = FakeUserRepository()
        role_repo = FakeRoleRepository()
        user_role_repo = FakeUserRoleRepository(role_repo, user_repo)
        await user_repo.add(_user("admin-1", "a1@example.com", deleted=True))
        await user_repo.add(_user("admin-2", "a2@example.com"))
        for user_id in ("admin-1", "admin-2"):
            await user_role_repo.add(
                UserRole(
                    id=f"{user_id}-role",
                    user_id=user_id,
                    role_id="role-admin",
                    assigned_by_user_id="admin",
                    assigned_at=NOW,
                    created_at=NOW,
                )
            )

        active = await user_role_repo.list_active_user_ids_for_role("role-admin")

        assert active == ["admin-2"]


class TestCategorySoftDeleteFiltering:
    async def test_soft_deleted_category_hidden(self):
        repo = FakeCategoryRepository()
        await repo.add(
            Category(
                id="cat-1",
                parent_category_id=None,
                category_key="design",
                name="Design",
                slug="design",
                description=None,
                is_active=True,
                sort_order=1,
                created_at=NOW,
                deleted_at=NOW,
            )
        )

        with pytest.raises(CategoryNotFoundError):
            await repo.get_by_id("cat-1")
        with pytest.raises(CategoryNotFoundError):
            await repo.get_by_slug("design")
        assert await repo.list_active() == []


class TestFreelancerProfileSoftDeleteFiltering:
    async def test_soft_deleted_profile_hidden(self):
        repo = FakeFreelancerProfileRepository()
        await repo.add(
            FreelancerProfile(
                id="profile-1",
                user_id="user-1",
                current_level_id=None,
                approval_status=FreelancerApprovalStatus.APPROVED,
                approved_by_user_id=None,
                approved_at=None,
                approval_note=None,
                display_name="Jane",
                headline=None,
                bio=None,
                country_code=None,
                city=None,
                timezone=None,
                hourly_rate_min=None,
                hourly_rate_max=None,
                is_available=True,
                deleted_at=NOW,
                created_at=NOW,
            )
        )

        with pytest.raises(FreelancerProfileNotFoundError):
            await repo.get_by_id("profile-1")
        with pytest.raises(FreelancerProfileNotFoundError):
            await repo.get_by_user_id("user-1")
        assert await repo.list_by_approval_status(FreelancerApprovalStatus.APPROVED) == []


class TestPortfolioItemSoftDelete:
    def _item(self, deleted: bool = False) -> PortfolioItem:
        return PortfolioItem(
            id="item-1",
            freelancer_profile_id="profile-1",
            title="Item",
            description=None,
            external_url=None,
            file_asset_id="file-1",
            display_order=0,
            is_featured=False,
            deleted_at=NOW if deleted else None,
            created_at=NOW,
        )

    async def test_soft_deleted_item_hidden(self):
        repo = FakePortfolioItemRepository()
        await repo.add(self._item(deleted=True))

        with pytest.raises(PortfolioItemNotFoundError):
            await repo.get_by_id("item-1")
        assert await repo.list_by_profile("profile-1") == []
        assert await repo.get_by_file_asset_id("file-1") is None

    async def test_entity_rejects_double_soft_delete(self):
        item = self._item()
        item.soft_delete(NOW)

        with pytest.raises(InvalidStateTransitionError):
            item.soft_delete(NOW)


class TestFormTemplateSoftDeleteFiltering:
    async def test_soft_deleted_template_hidden(self):
        repo = FakeFormTemplateRepository()
        await repo.add(
            FormTemplate(
                id="tpl-1",
                category_id="cat-1",
                template_key="brief",
                name="Brief",
                version_no=1,
                status=FormTemplateStatus.PUBLISHED,
                is_active=True,
                published_by_user_id=None,
                published_at=None,
                fields=[],
                created_at=NOW,
                deleted_at=NOW,
            )
        )

        with pytest.raises(FormTemplateNotFoundError):
            await repo.get_by_id("tpl-1")
        with pytest.raises(FormTemplateNotFoundError):
            await repo.get_published_for_category("cat-1")
        assert await repo.list_versions("cat-1", "brief") == []


class TestTicketingSoftDeleteFiltering:
    async def test_soft_deleted_ticket_hidden(self):
        repo = FakeTicketRepository()
        await repo.add(
            Ticket(
                id="ticket-1",
                ticket_code="TCK-2026-001",
                created_by_user_id="user-1",
                assigned_to_user_id=None,
                related_project_id=None,
                related_category_id=None,
                subject="Help",
                status=TicketStatus.OPEN,
                priority=TicketPriority.NORMAL,
                closed_by_user_id=None,
                closed_at=None,
                last_message_at=None,
                deleted_at=NOW,
                created_at=NOW,
            )
        )

        with pytest.raises(TicketNotFoundError):
            await repo.get_by_id("ticket-1")
        with pytest.raises(TicketNotFoundError):
            await repo.get_by_code("TCK-2026-001")
        assert await repo.list_for_user("user-1") == []

    async def test_soft_deleted_message_hidden_from_reads_but_visible_to_mutators(self):
        repo = FakeTicketMessageRepository()
        await repo.add(
            TicketMessage(
                id="message-1",
                ticket_id="ticket-1",
                sender_user_id="user-1",
                message_type=TicketMessageType.TEXT,
                body="hello",
                is_internal=False,
                sent_at=NOW,
                edited_at=None,
                deleted_at=NOW,
                attachment_file_asset_ids=["file-1"],
                created_at=NOW,
            )
        )

        assert await repo.list_by_ticket("ticket-1") == []
        assert await repo.list_by_file_asset_id("file-1") == []
        # get_by_id stays unfiltered on purpose so the entity guard can report a 409.
        assert (await repo.get_by_id("message-1")).id == "message-1"
