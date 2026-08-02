"""Project management application exceptions.

Domain-level exceptions (``ProjectNotFoundError``, ``ProjectLockedError``,
``FreelancerNotEligibleError``, ...) live in :mod:`app.domain.project.exceptions`.
Application-level errors (``PermissionDeniedError``, ``FormValidationError``) are shared
and defined in :mod:`app.application.shared.exceptions`.
"""
