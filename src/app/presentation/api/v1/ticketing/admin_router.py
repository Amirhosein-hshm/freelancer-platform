from fastapi import APIRouter, Depends

from app.application.ticketing.dto import CreateTicketOnBehalfCommand
from app.application.ticketing.use_cases.admin_create_ticket_on_behalf import (
    AdminCreateTicketOnBehalfUseCase,
)
from app.presentation.api.v1.ticketing.schemas import (
    AdminCreateTicketRequest,
    CreateTicketResponse,
)
from app.presentation.core.envelope import SuccessEnvelope
from app.presentation.core.providers import get_admin_create_ticket_on_behalf_use_case
from app.presentation.core.routes import DocumentedAPIRoute
from app.presentation.core.security import get_current_user

router = APIRouter(prefix="/admin/tickets", tags=["Admin - Ticketing"], route_class=DocumentedAPIRoute)


@router.post(
    "",
    response_model=SuccessEnvelope[CreateTicketResponse],
    status_code=201,
    operation_id="admin_create_ticket",
)
async def admin_create_ticket(
    payload: AdminCreateTicketRequest,
    current_user=Depends(get_current_user),
    use_case: AdminCreateTicketOnBehalfUseCase = Depends(get_admin_create_ticket_on_behalf_use_case),
) -> SuccessEnvelope[CreateTicketResponse]:
    result = await use_case.execute(
        CreateTicketOnBehalfCommand(
            actor_id=current_user.user_id,
            requester_user_id=payload.requester_user_id,
            target_user_id=payload.target_user_id,
            subject=payload.subject,
            related_project_id=payload.related_project_id,
            related_category_id=payload.related_category_id,
            priority=payload.priority,
        )
    )
    return SuccessEnvelope(
        message="Ticket created on behalf of user.",
        data=CreateTicketResponse(
            ticket_id=result.ticket_id,
            ticket_code=result.ticket_code,
            status=result.status,
        ),
    )
