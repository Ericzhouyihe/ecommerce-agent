from dataclasses import dataclass, field
from enum import Enum
from typing import Any


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

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "id": self.id,
            "title": self.title,
            "attributes": self.attributes,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MessageObject":
        return cls(
            type=data["type"],
            id=data["id"],
            title=data.get("title"),
            attributes=data.get("attributes", {}),
        )


@dataclass
class UserMessage:
    sender_id: str
    message_id: str
    type: MessageType = MessageType.TEXT
    text: str | None = None
    object: MessageObject | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "sender_id": self.sender_id,
            "message_id": self.message_id,
            "type": self.type.value,
            "text": self.text,
            "object": self.object.to_dict() if self.object else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "UserMessage":
        return cls(
            sender_id=data["sender_id"],
            message_id=data["message_id"],
            type=MessageType(data["type"]),
            text=data.get("text"),
            object=MessageObject.from_dict(data.get("object")) if data.get("object") else None,
        )


@dataclass
class BotMessage:
    text: str | None = None
    object: MessageObject | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "text": self.text,
            "object": self.object.to_dict() if self.object else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BotMessage":
        return cls(
            text=data.get("text"),
            object=MessageObject.from_dict(data.get("object")) if data.get("object") else None,
        )


@dataclass
class ProcessResult:
    sender_id: str
    message_id: str
    messages: list[BotMessage]
