from dataclasses import dataclass, field
from typing import Any

from shop_agent.domain.dialogue.messages import BotMessage, UserMessage


@dataclass
class Turn:
    # 一轮对话:用户的一条输入 + 机器人的若干条回复
    turn_id: str
    input_message: UserMessage
    assistant_messages: list[BotMessage]

    def to_dict(self) -> dict[str, Any]:
        return {
            "turn_id": self.turn_id,
            "input_message": self.input_message.to_dict(),
            "assistant_messages": [msg.to_dict() for msg in self.assistant_messages],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Turn":
        return cls(
            turn_id=data["turn_id"],
            input_message=UserMessage.from_dict(data["input_message"]),
            assistant_messages=[BotMessage.from_dict(msg) for msg in data["assistant_messages"]],
        )


@dataclass
class Session:
    # 一次会话(从 opening 到 closing)
    session_id: str
    started_at: float
    last_activity_at: float
    closed_at: float | None = None
    turns: list[Turn] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "started_at": self.started_at,
            "last_activity_at": self.last_activity_at,
            "closed_at": self.closed_at,
            "turns": [turn.to_dict() for turn in self.turns],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Session":
        return cls(
            session_id=data["session_id"],
            started_at=data["started_at"],
            last_activity_at=data["last_activity_at"],
            closed_at=data.get("closed_at"),
            turns=[Turn.from_dict(turn) for turn in data["turns"]],
        )
