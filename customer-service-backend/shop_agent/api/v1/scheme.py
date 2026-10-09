from typing import Any, Literal

from pydantic import BaseModel, Field


class ChatObject(BaseModel):
    type: str
    id: str
    title: str | None = None
    attributes: dict[str, Any] = Field(default_factory=dict)


class ChatRequest(BaseModel):
    sender_id: str
    text: str | None = None
    message_id: str | None = None
    object: ChatObject | None = None


class ChatBotMessage(BaseModel):
    text: str | None = None
    object: ChatObject | None = None


class ChatResponse(BaseModel):
    sender_id: str
    message_id: str
    messages: list[ChatBotMessage] = Field(default_factory=list)


# """历史消息条目：用户和机器人的消息混在同一个列表里，靠 role 区分"""
class HistoryMessage(BaseModel):
    role: Literal["user", "bot"]
    text: str | None = None
    object: ChatObject | None = None


class ChatHistoryResponse(BaseModel):
    sender_id: str
    messages: list[HistoryMessage] = Field(default_factory=list)
