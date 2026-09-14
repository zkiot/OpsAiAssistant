# app/api/v1/endpoints/ticket.py
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_ticket_service
from app.schemas.ticket import TicketCreateRequest, TicketListResponse, TicketOut
from app.services.ticket_service import TicketService

router = APIRouter()


@router.post("/tickets", response_model=TicketOut, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    request: TicketCreateRequest,
    ticket_service: TicketService = Depends(get_ticket_service),
) -> TicketOut:
    """创建工单。"""
    ticket = await ticket_service.create_ticket(
        server_ip=request.server_ip,
        title=request.title,
        description=request.description,
        severity=request.severity,
    )
    return TicketOut.model_validate(ticket)


@router.get("/tickets/{ticket_id}", response_model=TicketOut)
async def get_ticket(
    ticket_id: str,
    ticket_service: TicketService = Depends(get_ticket_service),
) -> TicketOut:
    """查询单个工单详情。"""
    ticket = await ticket_service.get_ticket(ticket_id)
    if ticket is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "工单不存在")
    return TicketOut.model_validate(ticket)


@router.get("/tickets", response_model=TicketListResponse)
async def list_tickets(
    server_ip: str | None = Query(None, description="按服务器IP过滤"),
    ticket_service: TicketService = Depends(get_ticket_service),
) -> TicketListResponse:
    """查询工单列表，支持按服务器IP过滤。"""
    if server_ip:
        items = await ticket_service.list_tickets_by_server(server_ip)
    else:
        items = await ticket_service.list_tickets()
    return TicketListResponse(total=len(items), items=[TicketOut.model_validate(t) for t in items])