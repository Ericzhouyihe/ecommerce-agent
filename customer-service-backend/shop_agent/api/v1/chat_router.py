from typing import Annotated

from fastapi import APIRouter, Depends

from shop_agent.api.dependencies import get_chat_service
from shop_agent.api.v1.scheme import (
    ChatRequest,
    ChatResponse,
    HistoryResponse,
)
from shop_agent.application.dialogue_service import DialogueService

router = APIRouter(prefix="/chat", tags=["智能客服"])


@router.post("", summary="发送消息并获取回复")
async def chat(
    message: ChatRequest,
    service: Annotated[DialogueService, Depends(get_chat_service)],
) -> ChatResponse:
    return await service.handle(message)


@router.get("/history", summary="获取聊天历史")
async def chat_history(
    sender_id: str,
    service: Annotated[DialogueService, Depends(get_chat_service)],
) -> HistoryResponse:
    return await service.get_history(sender_id)
