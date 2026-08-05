from fastapi import APIRouter, Depends

from app.application.ticketing.dto import (
    AssignTicketCommand,
    CloseTicketCommand,
    CreateTicketCommand,
    GetTicketMessagesQuery,
    GetUserTicketsQuery,
    SendMessageCommand,
    TicketMessageResult,
    TicketResult,
)
from app.application.ticketing.use_cases.assign_ticket import AssignTicketUseCase
from app.application.ticketing.use_cases.close_ticket import CloseTicketUseCase
from app.application.ticketing.use_cases.create_ticket import CreateTicketUseCase
from app.application.ticketing.use_cases.get_ticket_messages import GetTicketMessagesUseCase
from app.application.ticketing.use_cases.get_user_tickets import GetUserTicketsUseCase
from app.application.ticketing.use_cases.send_message import SendMessageUseCase
from app.presentation.api.v1.ticketing.schemas import (
    AssignTicketRequest,
    AssignTicketResponse,
    CloseTicketResponse,
    CreateTicketRequest,
    CreateTicketResponse,
    SendMessageRequest,
    SendMessageResponse,
    TicketMessageResponse,
    TicketResponse,
)
from app.presentation.core.envelope import SuccessEnvelope
from app.presentation.core.providers import (
    get_assign_ticket_use_case,
    get_close_ticket_use_case,
    get_create_ticket_use_case,
    get_get_ticket_messages_use_case,
    get_get_user_tickets_use_case,
    get_send_message_use_case,
)
from app.presentation.core.security import get_current_user

router = APIRouter(prefix="/tickets", tags=["Ticketing"])


def _to_ticket_response(result: TicketResult) -> TicketResponse:
    return TicketResponse(
        ticket_id=result.ticket_id,
        ticket_code=result.ticket_code,
        created_by_user_id=result.created_by_user_id,
        assigned_to_user_id=result.assigned_to_user_id,
        related_project_id=result.related_project_id,
        related_category_id=result.related_category_id,
        subject=result.subject,
        status=result.status,
        priority=result.priority,
        closed_at=result.closed_at,
        last_message_at=result.last_message_at,
    )


def _to_message_response(result: TicketMessageResult) -> TicketMessageResponse:
    return TicketMessageResponse(
        message_id=result.message_id,
        ticket_id=result.ticket_id,
        sender_user_id=result.sender_user_id,
        message_type=result.message_type,
        body=result.body,
        is_internal=result.is_internal,
        sent_at=result.sent_at,
        attachment_file_asset_ids=list(result.attachment_file_asset_ids),
    )


@router.post(
    "",
    response_model=SuccessEnvelope[CreateTicketResponse],
    status_code=201,
    operation_id="create_ticket",
)
async def create_ticket(
    payload: CreateTicketRequest,
    current_user=Depends(get_current_user),
    use_case: CreateTicketUseCase = Depends(get_create_ticket_use_case),
) -> SuccessEnvelope[CreateTicketResponse]:
    result = await use_case.execute(
        CreateTicketCommand(
            actor_id=current_user.user_id,
            subject=payload.subject,
            related_project_id=payload.related_project_id,
            related_category_id=payload.related_category_id,
            priority=payload.priority,
        )
    )
    return SuccessEnvelope(
        message="Ticket created.",
        data=CreateTicketResponse(
            ticket_id=result.ticket_id,
            ticket_code=result.ticket_code,
            status=result.status,
        ),
    )


@router.get(
    "",
    response_model=SuccessEnvelope[list[TicketResponse]],
    operation_id="get_user_tickets",
)
async def get_user_tickets(
    current_user=Depends(get_current_user),
    use_case: GetUserTicketsUseCase = Depends(get_get_user_tickets_use_case),
) -> SuccessEnvelope[list[TicketResponse]]:
    result = await use_case.execute(
        GetUserTicketsQuery(actor_id=current_user.user_id, user_id=current_user.user_id)
    )
    return SuccessEnvelope(
        message="User tickets.",
        data=[_to_ticket_response(t) for t in result.tickets],
    )


@router.get(
    "/{ticket_id}/messages",
    response_model=SuccessEnvelope[list[TicketMessageResponse]],
    operation_id="get_ticket_messages",
)
async def get_ticket_messages(
    ticket_id: str,
    current_user=Depends(get_current_user),
    use_case: GetTicketMessagesUseCase = Depends(get_get_ticket_messages_use_case),
) -> SuccessEnvelope[list[TicketMessageResponse]]:
    result = await use_case.execute(
        GetTicketMessagesQuery(actor_id=current_user.user_id, ticket_id=ticket_id)
    )
    return SuccessEnvelope(
        message="Ticket messages.",
        data=[_to_message_response(m) for m in result.messages],
    )


@router.post(
    "/{ticket_id}/messages",
    response_model=SuccessEnvelope[SendMessageResponse],
    status_code=201,
    operation_id="send_message",
)
async def send_message(
    ticket_id: str,
    payload: SendMessageRequest,
    current_user=Depends(get_current_user),
    use_case: SendMessageUseCase = Depends(get_send_message_use_case),
) -> SuccessEnvelope[SendMessageResponse]:
    result = await use_case.execute(
        SendMessageCommand(
            actor_id=current_user.user_id,
            ticket_id=ticket_id,
            body=payload.body,
            attachment_file_asset_ids=payload.attachment_file_asset_ids,
        )
    )
    return SuccessEnvelope(
        message="Message sent.",
        data=SendMessageResponse(
            message_id=result.message_id,
            ticket_id=result.ticket_id,
            last_message_at=result.last_message_at,
        ),
    )


@router.post(
    "/{ticket_id}/assign",
    response_model=SuccessEnvelope[AssignTicketResponse],
    operation_id="assign_ticket",
)
async def assign_ticket(
    ticket_id: str,
    payload: AssignTicketRequest,
    current_user=Depends(get_current_user),
    use_case: AssignTicketUseCase = Depends(get_assign_ticket_use_case),
) -> SuccessEnvelope[AssignTicketResponse]:
    result = await use_case.execute(
        AssignTicketCommand(
            actor_id=current_user.user_id,
            ticket_id=ticket_id,
            assignee_user_id=payload.assignee_user_id,
        )
    )
    return SuccessEnvelope(
        message="Ticket assigned.",
        data=AssignTicketResponse(
            ticket_id=result.ticket_id,
            assigned_to_user_id=result.assigned_to_user_id,
        ),
    )


@router.post(
    "/{ticket_id}/close",
    response_model=SuccessEnvelope[CloseTicketResponse],
    operation_id="close_ticket",
)
async def close_ticket(
    ticket_id: str,
    current_user=Depends(get_current_user),
    use_case: CloseTicketUseCase = Depends(get_close_ticket_use_case),
) -> SuccessEnvelope[CloseTicketResponse]:
    result = await use_case.execute(
        CloseTicketCommand(actor_id=current_user.user_id, ticket_id=ticket_id)
    )
    return SuccessEnvelope(
        message="Ticket closed.",
        data=CloseTicketResponse(ticket_id=result.ticket_id, status=result.status),
    )
