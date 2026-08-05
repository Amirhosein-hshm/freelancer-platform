from app.infrastructure.db.models import (  # noqa: F401  (register all models for Alembic autogenerate)
    category_models,
    feedback_models,
    form_models,
    freelancer_models,
    iam_models,
    project_models,
    review_models,
    sequence_models,
    ticketing_models,
)

__all__ = [
    "category_models",
    "feedback_models",
    "form_models",
    "freelancer_models",
    "iam_models",
    "project_models",
    "review_models",
    "sequence_models",
    "ticketing_models",
]
