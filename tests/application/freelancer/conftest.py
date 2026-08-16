from datetime import UTC, datetime

import pytest

from app.application.shared.ports import FileAssetContext, FileAssetMetadata
from app.domain.freelancer.entities import FreelancerLevel, FreelancerProfile, PortfolioItem
from app.domain.freelancer.enums import FreelancerApprovalStatus, FreelancerLevelAccessType
from tests.fakes.fake_file_storage import FakeFileStorageService
from tests.fakes.fake_freelancer_level_history_repository import FakeFreelancerLevelHistoryRepository
from tests.fakes.fake_freelancer_level_repository import FakeFreelancerLevelRepository
from tests.fakes.fake_freelancer_profile_repository import FakeFreelancerProfileRepository
from tests.fakes.fake_portfolio_item_repository import FakePortfolioItemRepository
from tests.fakes.fake_resume_repository import FakeResumeRepository

NOW = datetime(2026, 8, 2, tzinfo=UTC)


@pytest.fixture
def profile_repo() -> FakeFreelancerProfileRepository:
    return FakeFreelancerProfileRepository()


@pytest.fixture
def level_repo() -> FakeFreelancerLevelRepository:
    return FakeFreelancerLevelRepository()


@pytest.fixture
def level_history_repo() -> FakeFreelancerLevelHistoryRepository:
    return FakeFreelancerLevelHistoryRepository()


@pytest.fixture
def resume_repo() -> FakeResumeRepository:
    return FakeResumeRepository()


@pytest.fixture
def portfolio_item_repo() -> FakePortfolioItemRepository:
    return FakePortfolioItemRepository()


@pytest.fixture
def file_storage() -> FakeFileStorageService:
    return FakeFileStorageService()


@pytest.fixture
def make_asset(file_storage: FakeFileStorageService):
    def _make(
        asset_id: str = "asset-1",
        owner_user_id: str = "user-1",
        context: FileAssetContext = FileAssetContext.GENERIC,
        content: bytes = b"%PDF-1.4",
    ) -> str:
        file_storage.add(
            FileAssetMetadata(
                file_asset_id=asset_id,
                file_name="resume.pdf",
                size_bytes=len(content),
                mime_type="application/pdf",
                url=None,
                uploaded_at=NOW,
                owner_user_id=owner_user_id,
                context=context,
            ),
            content=content,
        )
        return asset_id

    return _make


@pytest.fixture
def make_level(level_repo: FakeFreelancerLevelRepository):
    async def _make(
        level_id: str = "level-1",
        level_key: str = "standard",
        **overrides: object,
    ) -> FreelancerLevel:
        fields: dict[str, object] = {
            "id": level_id,
            "level_key": level_key,
            "name": "Standard",
            "rank_order": 1,
            "access_type": FreelancerLevelAccessType.STANDARD,
            "min_completed_projects": 0,
            "min_rating": None,
            "max_active_applications": 3,
            "can_apply_public_projects": True,
            "can_apply_private_projects": False,
            "is_active": True,
            "created_at": NOW,
        }
        fields.update(overrides)
        level = FreelancerLevel(**fields)  # type: ignore[arg-type]
        await level_repo.add(level)
        return level

    return _make


@pytest.fixture
def make_profile(profile_repo: FakeFreelancerProfileRepository):
    async def _make(
        profile_id: str = "profile-1",
        user_id: str = "user-1",
        **overrides: object,
    ) -> FreelancerProfile:
        fields: dict[str, object] = {
            "id": profile_id,
            "user_id": user_id,
            "current_level_id": None,
            "approval_status": FreelancerApprovalStatus.PENDING,
            "approved_by_user_id": None,
            "approved_at": None,
            "approval_note": None,
            "display_name": "Jane Dev",
            "headline": None,
            "bio": None,
            "country_code": None,
            "city": None,
            "timezone": None,
            "hourly_rate_min": None,
            "hourly_rate_max": None,
            "is_available": True,
            "deleted_at": None,
            "created_at": NOW,
        }
        fields.update(overrides)
        profile = FreelancerProfile(**fields)  # type: ignore[arg-type]
        await profile_repo.add(profile)
        return profile

    return _make


@pytest.fixture
def make_portfolio_item(portfolio_item_repo: FakePortfolioItemRepository):
    async def _make(item_id: str = "item-1", profile_id: str = "profile-1", **overrides: object) -> PortfolioItem:
        fields: dict[str, object] = {
            "id": item_id,
            "freelancer_profile_id": profile_id,
            "title": "Portfolio Item",
            "description": None,
            "external_url": None,
            "file_asset_id": None,
            "display_order": 0,
            "is_featured": False,
            "deleted_at": None,
            "created_at": NOW,
        }
        fields.update(overrides)
        item = PortfolioItem(**fields)  # type: ignore[arg-type]
        await portfolio_item_repo.add(item)
        return item

    return _make
