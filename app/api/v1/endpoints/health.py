from fastapi import APIRouter, Depends
from app.api.deps import get_memory_service
from app.services.memory_service import MemoryService

router = APIRouter()


@router.get("/health", summary="检查健康状态")
async def health(memory_service: MemoryService = Depends(get_memory_service)) -> dict:
    return await memory_service.health()

@router.get("/stats", summary="系统统计")
async def stats(memory_service: MemoryService = Depends(get_memory_service),) -> dict:
    return await memory_service.stats()

