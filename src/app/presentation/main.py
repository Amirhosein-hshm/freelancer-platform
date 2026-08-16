from collections.abc import Sequence

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.presentation.api.v1.auth.router import router as auth_router
from app.presentation.api.v1.category.router import router as category_router
from app.presentation.api.v1.feedback.router import router as feedback_router
from app.presentation.api.v1.file.router import router as file_router
from app.presentation.api.v1.form.router import router as form_router
from app.presentation.api.v1.freelancer.admin_router import (
    level_router as admin_freelancer_level_router,
)
from app.presentation.api.v1.freelancer.admin_router import (
    router as admin_freelancer_router,
)
from app.presentation.api.v1.freelancer.router import router as freelancer_router
from app.presentation.api.v1.iam.catalog_router import router as iam_catalog_router
from app.presentation.api.v1.iam.router import router as iam_router
from app.presentation.api.v1.project.admin_router import router as admin_project_router
from app.presentation.api.v1.project.revisions_router import (
    router as project_revisions_router,
)
from app.presentation.api.v1.project.router import router as project_router
from app.presentation.api.v1.reporting.router import router as reporting_router
from app.presentation.api.v1.review.router import (
    deliveries_router as review_deliveries_router,
)
from app.presentation.api.v1.review.router import router as review_router
from app.presentation.api.v1.ticketing.admin_router import (
    router as admin_ticketing_router,
)
from app.presentation.api.v1.ticketing.router import router as ticketing_router
from app.presentation.core.error_handlers import register_exception_handlers
from app.presentation.core.routes import DocumentedAPIRoute
from app.presentation.websocket.router import router as websocket_router

API_PREFIX = "/api/v1"
DEFAULT_CORS_ORIGINS = ["http://localhost:3000"]


def create_app(cors_origins: Sequence[str] | None = None) -> FastAPI:
    app = FastAPI(
        title="Freelance Platform API",
        version="0.1.0",
        route_class=DocumentedAPIRoute,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(cors_origins) if cors_origins else DEFAULT_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_exception_handlers(app)

    for router in (
        auth_router,
        iam_router,
        iam_catalog_router,
        freelancer_router,
        admin_freelancer_router,
        admin_freelancer_level_router,
        category_router,
        file_router,
        form_router,
        project_router,
        admin_project_router,
        project_revisions_router,
        review_router,
        review_deliveries_router,
        feedback_router,
        ticketing_router,
        admin_ticketing_router,
        reporting_router,
    ):
        app.include_router(router, prefix=API_PREFIX)

    @app.get("/health", include_in_schema=False)
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(websocket_router)
    return app
