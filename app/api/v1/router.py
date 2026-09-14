from fastapi import APIRouter

from app.api.v1.endpoints import chat, health, knowledge_base,ticket

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(chat.router, tags=["chat"])
api_router.include_router(knowledge_base.router, tags=["knowledge_base"])
api_router.include_router(ticket.router, tags=["ticket"])
