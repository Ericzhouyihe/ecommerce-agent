from typing import Annotated

from fastapi import APIRouter, Depends

from shop_agent.api.dependencies import get_dialogue_service
from shop_agent.api.v1.mappers import build_chat_response, build_user_message, build_history_response
from shop_agent.api.v1.schemas import (
    ChatRequest,
    ChatResponse,
    HistoryResponse,
)
from shop_agent.application.dialogue_service import DialogueService
from shop_agent.domain.dialogue.messages import ProcessResult

router = APIRouter(prefix="/chat", tags=["智能客服"])


@router.post("", summary="发送消息并获取回复")
async def chat(
    message: ChatRequest,
    dialogue_service: Annotated[DialogueService, Depends(get_dialogue_service)],
) -> ChatResponse:

    process_result: ProcessResult = await dialogue_service.process_message(
        build_user_message(message)
    )

    return build_chat_response(process_result)


@router.get("/history", summary="获取聊天历史")
async def chat_history(
    sender_id: str,
    service: Annotated[DialogueService, Depends(get_dialogue_service)],
) -> HistoryResponse:
    state = await service.get_history(sender_id)
    return build_history_response(sender_id, state)