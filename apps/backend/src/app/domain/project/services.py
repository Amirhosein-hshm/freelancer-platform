from app.domain.freelancer.enums import FreelancerLevelEnum
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
    """Whether a freelancer (at ``current_level``) is allowed to apply to ``project``.

    Level comparison is hierarchical: ``current_level.rank() >= project.required_level.rank()``
    (SENIOR may apply to a JUNIOR-required project). ``current_level`` of ``None`` is
    ineligible whenever a ``required_level`` is set; a project with no ``required_level`` is
    open to everyone, including level-less freelancers. INVITE_ONLY projects are never
    self-applicable. ``MAX_ACTIVE_APPLICATIONS`` is a single global cap (the per-level
    ``max_active_applications`` knob was removed with the level table).
    """

    MAX_ACTIVE_APPLICATIONS = 10

    @staticmethod
    def is_eligible_to_apply(
        current_level: FreelancerLevelEnum | None,
        project: Project,
        active_application_count: int,
    ) -> bool:
        if project.visibility == ProjectVisibility.INVITE_ONLY:
            return False
        if active_application_count >= FreelancerEligibilityPolicy.MAX_ACTIVE_APPLICATIONS:
            return False
        if project.required_level is None:
            return True
        if current_level is None:
            return False
        return current_level.rank() >= project.required_level.rank()
