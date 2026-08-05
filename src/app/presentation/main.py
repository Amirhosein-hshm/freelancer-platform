from fastapi import FastAPI

from app.presentation.api.v1.auth.router import router as auth_router
from app.presentation.api.v1.category.router import router as category_router
from app.presentation.api.v1.feedback.router import router as feedback_router
from app.presentation.api.v1.form.router import router as form_router
from app.presentation.api.v1.freelancer.router import router as freelancer_router
from app.presentation.api.v1.iam.router import router as iam_router
from app.presentation.api.v1.project.router import router as project_router
from app.presentation.api.v1.reporting.router import router as reporting_router
from app.presentation.api.v1.review.router import (
    deliveries_router as review_deliveries_router,
)
from app.presentation.api.v1.review.router import router as review_router
from app.presentation.api.v1.ticketing.router import router as ticketing_router
from app.presentation.core.error_handlers import register_exception_handlers
from app.presentation.websocket.router import router as websocket_router

API_PREFIX = "/api/v1"


def create_app() -> FastAPI:
    app = FastAPI(
        title="Freelance Platform API",
        version="0.1.0",
    )
    register_exception_handlers(app)

    for router in (
        auth_router,
        iam_router,
        freelancer_router,
        category_router,
        form_router,
        project_router,
        review_router,
        review_deliveries_router,
        feedback_router,
        ticketing_router,
        reporting_router,
    ):
        app.include_router(router, prefix=API_PREFIX)

    app.include_router(websocket_router)
    return app