from typing import Any, Literal

from pydantic import BaseModel, Field


class ChatObjectRequest(BaseModel):
    type: str
    id: str
    title: str
    attributes: dict[str, Any] = Field(default_factory=dict)


class ChatRequest(BaseModel):  # 请求
    sender_id: str
    text: str
    message_id: str
    object: ChatObjectRequest | None = None


class ReplyMessage(BaseModel):  # ★ 单条回复
    text: str
    object: ChatObjectRequest | None = None


class ChatResponse(BaseModel):  # ★ 整体响应
    sender_id: str
    message_id: str
    messages: list[ReplyMessage] = Field(default_factory=list)


# """历史消息条目：用户和机器人的消息混在同一个列表里，靠 role 区分"""
class HistoryMessage(BaseModel):
    role: Literal["user", "bot"]  # 只允许这两个值
    text: str | None = None  # 文档标注 可空
    object: ChatObjectRequest | None = None


class ChatHistoryResponse(BaseModel):
    sender_id: str
    messages: list[HistoryMessage] = Field(default_factory=list)
