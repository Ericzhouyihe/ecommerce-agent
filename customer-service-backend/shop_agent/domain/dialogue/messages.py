from dataclasses import dataclass, field
from enum import Enum


class MessageType(Enum):
    TEXT = "text"
    OBJECT = "object"


@dataclass
class MessageObject:
    # FocusedObject
    type: str
    id: str
    title: str | None = None
    attributes: dict = field(default_factory=dict)


@dataclass
class UserMessage:
    sender_id: str
    message_id: str
    type: MessageType = MessageType.TEXT
    text: str | None = None
    object: MessageObject | None = None


@dataclass
class BotMessage:
    text: str | None = None
    object: MessageObject | None = None


@dataclass
class ProcessResult:
    sender_id: str
    message_id: str
    messages: list[BotMessage]
