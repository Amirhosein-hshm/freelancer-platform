from app.domain.freelancer.entities import FreelancerLevel
from app.domain.project.entities import Project, ProjectRevisionRequest
from app.domain.project.enums import ProjectVisibility
from app.domain.project.exceptions import MaxRevisionsExceededError


class RevisionPolicy:
    """Maximum allowed revision rounds per project."""

    MAX_REVISIONS = 3

    @staticmethod
    def can_request_new_revision(existing_requests: list[ProjectRevisionRequest]) -> bool:
        return len(existing_requests) < RevisionPolicy.MAX_REVISIONS

    @staticmethod
    def ensure_can_request_new_revision(existing_requests: list[ProjectRevisionRequest]) -> None:
        if not RevisionPolicy.can_request_new_revision(existing_requests):
            raise MaxRevisionsExceededError(
                f"Project has reached the maximum of {RevisionPolicy.MAX_REVISIONS} revisions."
            )


class FreelancerEligibilityPolicy:
    """Whether a freelancer (at ``level``) is allowed to apply to ``project``."""

    @staticmethod
    def is_eligible_to_apply(
        level: FreelancerLevel,
        project: Project,
        active_application_count: int,
    ) -> bool:
        if not level.is_active:
            return False
        if project.visibility == ProjectVisibility.PUBLIC and not level.can_apply_public_projects:
            return False
        if project.visibility == ProjectVisibility.PRIVATE and not level.can_apply_private_projects:
            return False
        if project.visibility == ProjectVisibility.INVITE_ONLY:
            return False
        return not (
            level.max_active_applications is not None and active_application_count >= level.max_active_applications
        )
