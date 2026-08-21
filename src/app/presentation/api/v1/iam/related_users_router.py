from fastapi import APIRouter, Depends

from app.application.shared.pagination import total_pages
from app.application.ticketing.dto import ListRelatedUsersQuery
from app.application.ticketing.use_cases.list_related_users import ListRelatedUsersUseCase
from app.presentation.api.v1.iam.schemas import RelatedUserResponse
from app.presentation.core.envelope import PaginationMeta, SuccessEnvelope
from app.presentation.core.pagination import PageQuery
from app.presentation.core.providers import get_list_related_users_use_case
from app.presentation.core.routes import DocumentedAPIRoute
from app.presentation.core.security import get_current_user

router = APIRouter(prefix="/users", tags=["Users"], route_class=DocumentedAPIRoute)


@router.get(
    "/related",
    response_model=SuccessEnvelope[list[RelatedUserResponse]],
    operation_id="list_related_users",
)
async def list_related_users(
    current_user=Depends(get_current_user),
    pagination: PageQuery = Depends(),
    use_case: ListRelatedUsersUseCase = Depends(get_list_related_users_use_case),
) -> SuccessEnvelope[list[RelatedUserResponse]]:
    result = await use_case.execute(
        ListRelatedUsersQuery(
            actor_id=current_user.user_id,
            user_id=current_user.user_id,
            page=pagination.page,
            page_size=pagination.page_size,
        )
    )
    return SuccessEnvelope(
        message="Related users.",
        data=[
            RelatedUserResponse(
                user_id=user.user_id,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
            )
            for user in result.users
        ],
        meta=PaginationMeta(
            page=result.page,
            page_size=result.page_size,
            total_items=result.total_items,
            total_pages=total_pages(result.total_items, result.page_size),
        ),
    )