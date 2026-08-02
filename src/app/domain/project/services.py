from app.domain.freelancer.entities import FreelancerLevel
from app.domain.project.entities import Project, ProjectRevisionRequest
from app.domain.project.enums import ProjectVisibility


class RevisionPolicy:
    """Maximum allowed revision rounds per project."""

    MAX_REVISIONS = 3

    @staticmethod
    def can_request_new_revision(existing_requests: list[ProjectRevisionRequest]) -> bool:
        return len(existing_requests) < RevisionPolicy.MAX_REVISIONS


class FreelancerEligibilityPolicy:
    """Whether a freelancer (at ``level``) is allowed to apply to ``project``."""

    @staticmethod
    def is_eligible_to_apply(
        level: FreelancerLevel,
        project: Project,
        active_application_count: int,
    ) -> bool:
        if project.visibility == ProjectVisibility.PUBLIC and not level.can_apply_public_projects:
            return False
        if project.visibility == ProjectVisibility.PRIVATE and not level.can_apply_private_projects:
            return False
        if project.visibility == ProjectVisibility.INVITE_ONLY:
            return False
        return not (
            level.max_active_applications is not None
            and active_application_count >= level.max_active_applications
        )
