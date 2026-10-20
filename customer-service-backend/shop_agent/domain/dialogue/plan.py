from dataclasses import dataclass, field
from enum import Enum


class TurnKind(Enum):
    CHITCHAT = "chitchat"  # 闲聊
    KNOWLEDGE = "knowledge"  # 知识问答
    TASK = "task"  # 业务任务(要推进 flow)
    INVALID = "invalid"  # 听不懂 / 无法处理


@dataclass
class TurnPlan:
    kind: TurnKind = TurnKind.INVALID
    flow_id: str | None = None  # kind == TASK 时必填
    slots: dict = field(default_factory=dict)  # 本轮抽取到的槽位
    reason: str | None = None  # 为什么判定成 INVALID,便于调试
