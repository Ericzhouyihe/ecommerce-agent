import uuid

from shop_agent.api.v1.scheme import (
    ChatBotMessage,
    ChatObject,
    ChatRequest,
    ChatResponse,
    HistoryMessage,
    HistoryResponse,
)
from shop_agent.domain.dialogue.messages import (
    MessageObject,
    MessageType,
    ProcessResult,
    UserMessage,
)
from shop_agent.domain.dialogue.state import DialogueState


def _to_message_object(chat_object: ChatObject | None) -> MessageObject | None:
    if chat_object is None:
        return None
    return MessageObject(
        type=chat_object.type,
        id=chat_object.id,
        title=chat_object.title,
        attributes=chat_object.attributes,
    )


def _to_chat_object(message_object: MessageObject | None) -> ChatObject | None:
    if message_object is None:
        return None
    return ChatObject(
        type=message_object.type,
        id=message_object.id,
        title=message_object.title,
        attributes=message_object.attributes,
    )


def build_user_message(chat_request: ChatRequest) -> UserMessage:
    return UserMessage(
        sender_id=chat_request.sender_id,
        message_id=chat_request.message_id or str(uuid.uuid4()),
        type=MessageType.TEXT if chat_request.text else MessageType.OBJECT,
        text=chat_request.text,
        object=_to_message_object(chat_request.object),
    )


def build_chat_response(process_result: ProcessResult) -> ChatResponse:
    return ChatResponse(
        sender_id=process_result.sender_id,
        message_id=process_result.message_id,
        messages=[
            ChatBotMessage(text=m.text, object=_to_chat_object(m.object))
            for m in process_result.messages
        ],
    )


def build_history_response(
    sender_id: str, state: DialogueState
) -> HistoryResponse:
    """把整个 DialogueState 的会话历史摊平成 user/bot 消息列表。"""
    messages: list[HistoryMessage] = []
    for session in state.sessions:
        for turn in session.turns:
            user_message = turn.user_message
            messages.append(
                HistoryMessage(
                    role="user",
                    text=user_message.text,
                    object=_to_chat_object(user_message.object),
                )
            )
            for bot_message in turn.bot_messages:
                messages.append(
                    HistoryMessage(
                        role="bot",
                        text=bot_message.text,
                        object=_to_chat_object(bot_message.object),
                    )
                )
    return HistoryResponse(sender_id=sender_id, messages=messages)
