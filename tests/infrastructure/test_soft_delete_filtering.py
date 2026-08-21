"""Integration tests for soft-delete filtering against a real Postgres (task §2).

These assert the actual SQL WHERE clauses, not the in-memory fakes: for every entity
carrying ``deleted_at``, a soft-deleted row must vanish from every read path.
"""

from datetime import UTC, datetime
from decimal import Decimal

import pytest

from app.domain.category.exceptions import CategoryNotFoundError
from app.domain.form.enums import FormTemplateStatus
from app.domain.form.exceptions import FormTemplateNotFoundError
from app.domain.freelancer.enums import FreelancerApprovalStatus
from app.domain.freelancer.exceptions import (
    FreelancerProfileNotFoundError,
    PortfolioItemNotFoundError,
)
from app.domain.iam.enums import UserStatus
from app.domain.iam.exceptions import UserNotFoundError
from app.domain.iam.value_objects import Email
from app.domain.project.enums import ProjectStatus
from app.domain.project.exceptions import ProjectNotFoundError
from app.domain.project.value_objects import ProjectCode
from app.domain.ticketing.exceptions import TicketNotFoundError
from app.infrastructure.db.models.category_models import CategoryModel
from app.infrastructure.db.models.form_models import FormTemplateModel
from app.infrastructure.db.models.freelancer_models import (
    FreelancerProfileModel,
    PortfolioItemModel,
)
from app.infrastructure.db.models.iam_models import RoleModel, UserModel, UserRoleModel
from app.infrastructure.db.models.project_models import ProjectModel
from app.infrastructure.db.models.ticketing_models import TicketMessageModel, TicketModel
from app.infrastructure.repositories.category_repository import SqlAlchemyCategoryRepository
from app.infrastructure.repositories.form_template_repository import SqlAlchemyFormTemplateRepository
from app.infrastructure.repositories.freelancer_profile_repository import (
    SqlAlchemyFreelancerProfileRepository,
)
from app.infrastructure.repositories.portfolio_item_repository import SqlAlchemyPortfolioItemRepository
from app.infrastructure.repositories.project_repository import SqlAlchemyProjectRepository
from app.infrastructure.repositories.ticket_message_repository import SqlAlchemyTicketMessageRepository
from app.infrastructure.repositories.ticket_repository import SqlAlchemyTicketRepository
from app.infrastructure.repositories.user_repository import SqlAlchemyUserRepository
from app.infrastructure.repositories.user_role_repository import SqlAlchemyUserRoleRepository

pytestmark = pytest.mark.integration

NOW = datetime(2026, 8, 2, tzinfo=UTC)
DELETED = datetime(2026, 8, 3, tzinfo=UTC)

# NOTE: models inheriting TimestampMixin declare created_at WITHOUT timezone=True and rely on
# a server default, so those inserts omit created_at. Models in iam_models/ticketing_models
# declare created_at as DateTime(timezone=True) and require an explicit aware value.


def _user_model(user_id: str, email: str, deleted: bool) -> UserModel:
    return UserModel(
        id=user_id,
        email=email,
        phone=None,
        password_hash="hash",
        first_name="Jane",
        last_name="Doe",
        status=UserStatus.ACTIVE.value,
        created_at=NOW,
        deleted_at=DELETED if deleted else None,
    )


class TestUserRepositorySoftDelete:
    async def test_soft_deleted_user_excluded_from_all_reads(self, db_session):
        db_session.add(_user_model("u-del", "deleted@example.com", deleted=True))
        db_session.add(_user_model("u-live", "live@example.com", deleted=False))
        await db_session.commit()
        repo = SqlAlchemyUserRepository(db_session)

        with pytest.raises(UserNotFoundError):
            await repo.get_by_id("u-del")
        assert await repo.find_by_id("u-del") is None
        with pytest.raises(UserNotFoundError):
            await repo.get_by_email(Email("deleted@example.com"))
        assert await repo.exists_by_email(Email("deleted@example.com")) is False
        assert [u.id for u in await repo.list_all(limit=10, offset=0)] == ["u-live"]
        assert [u.id for u in await repo.list_by_status(UserStatus.ACTIVE, limit=10, offset=0)] == ["u-live"]
        assert await repo.count_all() == 1
        assert await repo.count_all(UserStatus.ACTIVE) == 1

    async def test_email_of_soft_deleted_user_still_registered(self, db_session):
        db_session.add(_user_model("u-del", "deleted@example.com", deleted=True))
        await db_session.commit()
        repo = SqlAlchemyUserRepository(db_session)

        assert await repo.email_exists_including_deleted(Email("deleted@example.com")) is True
        assert await repo.exists_by_email(Email("deleted@example.com")) is False


class TestUserRoleRepositorySoftDelete:
    async def test_soft_deleted_admin_not_counted_as_active_admin(self, db_session):
        db_session.add(RoleModel(id="role-admin", role_key="admin", name="Admin", is_system=True, created_at=NOW))
        db_session.add(_user_model("admin-del", "a1@example.com", deleted=True))
        db_session.add(_user_model("admin-live", "a2@example.com", deleted=False))
        await db_session.flush()
        for user_id in ("admin-del", "admin-live"):
            db_session.add(
                UserRoleModel(
                    id=f"ur-{user_id}",
                    user_id=user_id,
                    role_id="role-admin",
                    assigned_by_user_id="admin-live",
                    assigned_at=NOW,
                    is_active=True,
                    created_at=NOW,
                )
            )
        await db_session.commit()
        repo = SqlAlchemyUserRoleRepository(db_session)

        assert await repo.list_active_user_ids_for_role("role-admin") == ["admin-live"]


class TestCategoryRepositorySoftDelete:
    async def test_soft_deleted_category_excluded(self, db_session):
        db_session.add(
            CategoryModel(
                id="cat-del",
                parent_category_id=None,
                category_key="design",
                name="Design",
                slug="design",
                description=None,
                is_active=True,
                sort_order=1,
                deleted_at=DELETED,
            )
        )
        await db_session.commit()
        repo = SqlAlchemyCategoryRepository(db_session)

        with pytest.raises(CategoryNotFoundError):
            await repo.get_by_id("cat-del")
        with pytest.raises(CategoryNotFoundError):
            await repo.get_by_slug("design")
        assert await repo.list_active() == []
        assert await repo.list_by_parent_id("cat-del") == []


class TestFreelancerProfileRepositorySoftDelete:
    async def test_soft_deleted_profile_excluded(self, db_session):
        db_session.add(_user_model("user-1", "f1@example.com", deleted=False))
        await db_session.flush()
        db_session.add(
            FreelancerProfileModel(
                id="profile-del",
                user_id="user-1",
                current_level_id=None,
                approval_status=FreelancerApprovalStatus.APPROVED.value,
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
                deleted_at=DELETED,
            )
        )
        await db_session.commit()
        repo = SqlAlchemyFreelancerProfileRepository(db_session)

        with pytest.raises(FreelancerProfileNotFoundError):
            await repo.get_by_id("profile-del")
        with pytest.raises(FreelancerProfileNotFoundError):
            await repo.get_by_user_id("user-1")
        assert await repo.list_by_approval_status(FreelancerApprovalStatus.APPROVED) == []


class TestPortfolioItemRepositorySoftDelete:
    async def test_soft_deleted_item_excluded(self, db_session):
        db_session.add(_user_model("user-1", "f1@example.com", deleted=False))
        await db_session.flush()
        db_session.add(
            FreelancerProfileModel(
                id="profile-1",
                user_id="user-1",
                current_level_id=None,
                approval_status=FreelancerApprovalStatus.APPROVED.value,
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
                deleted_at=None,
            )
        )
        await db_session.flush()
        db_session.add(
            PortfolioItemModel(
                id="item-del",
                freelancer_profile_id="profile-1",
                title="Item",
                description=None,
                external_url=None,
                file_asset_id="file-1",
                display_order=0,
                is_featured=False,
                deleted_at=DELETED,
            )
        )
        await db_session.commit()
        repo = SqlAlchemyPortfolioItemRepository(db_session)

        with pytest.raises(PortfolioItemNotFoundError):
            await repo.get_by_id("item-del")
        assert await repo.list_by_profile("profile-1") == []
        assert await repo.get_by_file_asset_id("file-1") is None


class TestFormTemplateRepositorySoftDelete:
    async def test_soft_deleted_template_excluded(self, db_session):
        db_session.add(
            CategoryModel(
                id="cat-1",
                parent_category_id=None,
                category_key="design",
                name="Design",
                slug="design",
                description=None,
                is_active=True,
                sort_order=1,
                deleted_at=None,
            )
        )
        await db_session.flush()
        db_session.add(
            FormTemplateModel(
                id="tpl-del",
                category_id="cat-1",
                template_key="brief",
                name="Brief",
                version_no=1,
                status=FormTemplateStatus.PUBLISHED.value,
                is_active=True,
                published_by_user_id=None,
                published_at=None,
                deleted_at=DELETED,
            )
        )
        await db_session.commit()
        repo = SqlAlchemyFormTemplateRepository(db_session)

        with pytest.raises(FormTemplateNotFoundError):
            await repo.get_by_id("tpl-del")
        with pytest.raises(FormTemplateNotFoundError):
            await repo.get_published_for_category("cat-1")
        assert await repo.list_versions("cat-1", "brief") == []


class TestProjectRepositorySoftDelete:
    async def _seed_project(self, db_session, deleted: bool) -> None:
        db_session.add(_user_model("cust-1", "c1@example.com", deleted=False))
        db_session.add(
            CategoryModel(
                id="cat-1",
                parent_category_id=None,
                category_key="design",
                name="Design",
                slug="design",
                description=None,
                is_active=True,
                sort_order=1,
                deleted_at=None,
            )
        )
        await db_session.flush()
        db_session.add(
            FormTemplateModel(
                id="tpl-1",
                category_id="cat-1",
                template_key="brief",
                name="Brief",
                version_no=1,
                status=FormTemplateStatus.PUBLISHED.value,
                is_active=True,
                published_by_user_id=None,
                published_at=None,
                deleted_at=None,
            )
        )
        await db_session.flush()
        db_session.add(
            ProjectModel(
                id="prj-del",
                project_code="PRJ-2026-001",
                customer_user_id="cust-1",
                category_id="cat-1",
                form_template_id="tpl-1",
                assigned_supervisor_user_id="cust-1",
                selected_application_id=None,
                title="Project",
                description="Desc",
                visibility="public",
                priority="normal",
                budget_type="fixed",
                fixed_amount=Decimal("100.00"),
                min_amount=None,
                max_amount=None,
                currency_code="USD",
                status=ProjectStatus.PUBLISHED.value,
                application_deadline=None,
                start_at=None,
                due_at=None,
                completed_at=None,
                cancelled_at=None,
                locked_at=None,
                deleted_at=DELETED if deleted else None,
            )
        )
        await db_session.commit()

    async def test_soft_deleted_project_excluded(self, db_session):
        await self._seed_project(db_session, deleted=True)
        repo = SqlAlchemyProjectRepository(db_session)

        with pytest.raises(ProjectNotFoundError):
            await repo.get_by_id("prj-del")
        with pytest.raises(ProjectNotFoundError):
            await repo.get_by_code(ProjectCode("PRJ-2026-001"))
        assert await repo.list_by_customer("cust-1") == []
        assert await repo.list_by_supervisor("cust-1") == []
        assert await repo.list_by_category("cat-1") == []
        assert await repo.count_active_by_category("cat-1") == 0
        assert await repo.count_active_by_form_template("tpl-1") == 0

    async def test_live_project_still_visible(self, db_session):
        await self._seed_project(db_session, deleted=False)
        repo = SqlAlchemyProjectRepository(db_session)

        assert (await repo.get_by_id("prj-del")).id == "prj-del"
        assert [p.id for p in await repo.list_by_customer("cust-1")] == ["prj-del"]
        assert await repo.count_active_by_category("cat-1") == 1

    async def test_form_template_soft_delete_survives_project_fk(self, db_session):
        """DeleteFormTemplate is allowed while only terminal projects reference the template.
        A hard delete would violate projects.form_template_id; a soft delete cannot."""
        await self._seed_project(db_session, deleted=False)
        repo = SqlAlchemyFormTemplateRepository(db_session)
        template = await repo.get_by_id("tpl-1")

        template.soft_delete(DELETED)
        await repo.update(template)
        await db_session.commit()

        with pytest.raises(FormTemplateNotFoundError):
            await repo.get_by_id("tpl-1")
        # The referencing project row is untouched and still readable.
        assert (await SqlAlchemyProjectRepository(db_session).get_by_id("prj-del")).form_template_id == "tpl-1"


class TestTicketingRepositorySoftDelete:
    async def _seed_ticket(self, db_session) -> None:
        db_session.add(_user_model("user-1", "t1@example.com", deleted=False))
        await db_session.flush()
        db_session.add(
            TicketModel(
                id="ticket-del",
                ticket_code="TCK-2026-001",
                created_by_user_id="user-1",
                assigned_to_user_id=None,
                related_project_id=None,
                related_category_id=None,
                subject="Help",
                status="open",
                priority="normal",
                closed_by_user_id=None,
                closed_at=None,
                last_message_at=None,
                created_at=NOW,
                deleted_at=DELETED,
            )
        )
        await db_session.commit()

    async def test_soft_deleted_ticket_excluded(self, db_session):
        await self._seed_ticket(db_session)
        repo = SqlAlchemyTicketRepository(db_session)

        with pytest.raises(TicketNotFoundError):
            await repo.get_by_id("ticket-del")
        with pytest.raises(TicketNotFoundError):
            await repo.get_by_code("TCK-2026-001")
        assert await repo.list_for_user("user-1") == []

    async def test_soft_deleted_message_excluded_from_list_reads(self, db_session):
        db_session.add(_user_model("user-1", "t1@example.com", deleted=False))
        await db_session.flush()
        db_session.add(
            TicketModel(
                id="ticket-1",
                ticket_code="TCK-2026-002",
                created_by_user_id="user-1",
                assigned_to_user_id=None,
                related_project_id=None,
                related_category_id=None,
                subject="Help",
                status="open",
                priority="normal",
                closed_by_user_id=None,
                closed_at=None,
                last_message_at=None,
                created_at=NOW,
                deleted_at=None,
            )
        )
        await db_session.flush()
        db_session.add(
            TicketMessageModel(
                id="msg-del",
                ticket_id="ticket-1",
                sender_user_id="user-1",
                message_type="text",
                body="hello",
                is_internal=False,
                sent_at=NOW,
                edited_at=None,
                attachment_file_asset_ids=["file-1"],
                created_at=NOW,
                deleted_at=DELETED,
            )
        )
        await db_session.commit()
        repo = SqlAlchemyTicketMessageRepository(db_session)

        assert await repo.list_by_ticket("ticket-1") == []
        assert await repo.list_by_file_asset_id("file-1") == []
        # get_by_id is unfiltered by design so the entity guard can raise a 409.
        assert (await repo.get_by_id("msg-del")).id == "msg-del"

    async def test_list_by_file_asset_id_matches_live_attachment(self, db_session):
        """Regression: these columns were JSON, so the containment predicate compiled to a
        LIKE that Postgres rejects (``operator does not exist: json ~~ text``), making every
        ticket-attachment file-access check raise a 500. They are JSONB now."""
        db_session.add(_user_model("user-1", "t1@example.com", deleted=False))
        await db_session.flush()
        db_session.add(
            TicketModel(
                id="ticket-1",
                ticket_code="TCK-2026-003",
                created_by_user_id="user-1",
                assigned_to_user_id=None,
                related_project_id=None,
                related_category_id=None,
                subject="Help",
                status="open",
                priority="normal",
                closed_by_user_id=None,
                closed_at=None,
                last_message_at=None,
                created_at=NOW,
                deleted_at=None,
            )
        )
        await db_session.flush()
        db_session.add(
            TicketMessageModel(
                id="msg-live",
                ticket_id="ticket-1",
                sender_user_id="user-1",
                message_type="text",
                body="see attachment",
                is_internal=False,
                sent_at=NOW,
                edited_at=None,
                attachment_file_asset_ids=["file-1", "file-2"],
                created_at=NOW,
                deleted_at=None,
            )
        )
        await db_session.commit()
        repo = SqlAlchemyTicketMessageRepository(db_session)

        assert [m.id for m in await repo.list_by_file_asset_id("file-1")] == ["msg-live"]
        assert [m.id for m in await repo.list_by_file_asset_id("file-2")] == ["msg-live"]
        assert await repo.list_by_file_asset_id("file-absent") == []
