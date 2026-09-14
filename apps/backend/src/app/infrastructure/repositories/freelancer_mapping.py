from app.domain.freelancer.entities import (
    FreelancerLevelHistory,
    FreelancerProfile,
    PortfolioItem,
    Resume,
)
from app.domain.freelancer.enums import (
    FreelancerApprovalStatus,
    FreelancerLevelEnum,
)


def to_domain_freelancer_profile(row: object) -> FreelancerProfile:
    return FreelancerProfile(
        id=row.id,
        created_at=row.created_at,
        updated_at=row.updated_at,
        user_id=row.user_id,
        current_level=FreelancerLevelEnum(row.current_level) if row.current_level else None,
        approval_status=FreelancerApprovalStatus(row.approval_status),
        approved_by_user_id=row.approved_by_user_id,
        approved_at=row.approved_at,
        approval_note=row.approval_note,
        display_name=row.display_name,
        headline=row.headline,
        bio=row.bio,
        country_code=row.country_code,
        city=row.city,
        timezone=row.timezone,
        hourly_rate_min=row.hourly_rate_min,
        hourly_rate_max=row.hourly_rate_max,
        is_available=row.is_available,
        deleted_at=row.deleted_at,
        created_by_user_id=row.created_by_user_id,
    )


def to_domain_freelancer_level_history(row: object) -> FreelancerLevelHistory:
    return FreelancerLevelHistory(
        id=row.id,
        created_at=row.created_at,
        updated_at=row.updated_at,
        freelancer_profile_id=row.freelancer_profile_id,
        old_level=FreelancerLevelEnum(row.old_level) if row.old_level else None,
        new_level=FreelancerLevelEnum(row.new_level),
        assigned_by_user_id=row.assigned_by_user_id,
        reason=row.reason,
        assigned_at=row.assigned_at,
    )


def to_domain_resume(row: object) -> Resume:
    return Resume(
        id=row.id,
        created_at=row.created_at,
        updated_at=row.updated_at,
        freelancer_profile_id=row.freelancer_profile_id,
        file_asset_id=row.file_asset_id,
        version_no=row.version_no,
        summary=row.summary,
        is_current=row.is_current,
    )


def to_domain_portfolio_item(row: object) -> PortfolioItem:
    return PortfolioItem(
        id=row.id,
        created_at=row.created_at,
        updated_at=row.updated_at,
        freelancer_profile_id=row.freelancer_profile_id,
        title=row.title,
        description=row.description,
        external_url=row.external_url,
        file_asset_id=row.file_asset_id,
        display_order=row.display_order,
        is_featured=row.is_featured,
        deleted_at=row.deleted_at,
    )