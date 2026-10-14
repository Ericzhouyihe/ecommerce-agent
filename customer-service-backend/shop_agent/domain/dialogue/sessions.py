from dataclasses import dataclass, field

from shop_agent.domain.dialogue.messages import BotMessage, UserMessage


@dataclass
class Turn:
    # 一轮对话:用户的一条输入 + 机器人的若干条回复
    turn_id: str
    input_message: UserMessage
    assistant_messages: list[BotMessage]


@dataclass
class Session:
    # 一次会话(从 opening 到 closing)
    session_id: str
    started_at: float
    last_activity_at: float
    closed_at: float | None = None
    turns: list[Turn] = field(default_factory=list)
