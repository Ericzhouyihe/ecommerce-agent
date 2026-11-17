from dataclasses import dataclass, field
from enum import Enum

from shop_agent.domain.task.command.commands import Command


@dataclass
class TaskTurnPlan:
    commands: list[Command] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> "TaskTurnPlan":
        return cls(commands=[Command.from_dict(c) for c in data["commands"]])


@dataclass
class KnowledgeTurnPlan:
    intents: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> "KnowledgeTurnPlan":
        return cls(intents=data["intents"])


@dataclass
class ChitchatTurnPlan:
    pass


@dataclass(slots=True)
class TurnPlan:
    """一轮对话的执行计划:task / knowledge / chitchat 三条轨道最多同时命中一条。"""

    task: TaskTurnPlan | None = None
    knowledge: KnowledgeTurnPlan | None = None
    chitchat: ChitchatTurnPlan | None = None

    @classmethod
    def from_dict(cls, data: dict) -> "TurnPlan":
        return cls(
            task=TaskTurnPlan.from_dict(data["task"])
            if data.get("task") is not None
            else None,
            knowledge=KnowledgeTurnPlan.from_dict(data["knowledge"])
            if data.get("knowledge") is not None
            else None,
            chitchat=ChitchatTurnPlan() if data.get("chitchat") is not None else None,
        )


class ClarifyReason(str, Enum):
    """需要向用户澄清的原因。"""

    MISSING_TRACK = "missing_track"  # 三条轨道一个都没命中
    MULTIPLE_TRACKS = "multiple_tracks"  # 同时命中多条轨道
    MISSING_TASK_COMMANDS = "missing_task_commands"  # task 轨道没有 commands
    MISSING_KNOWLEDGE_INTENT = "missing_knowledge_intent"  # knowledge 轨道没有 intents
    MISSING_FOCUSED_OBJECT = "missing_focused_object"  # 意图需要聚焦对象但用户没提供
    OBJECT_REQUIRES_INTENT = "object_requires_intent"  # 发了对象但没说要干什么
    INVALID_TASK_TARGET = "invalid_task_target"  # 要启动/恢复的流程不存在或未挂起
    NO_ACTIVE_TASK = "no_active_task"  # 没有进行中的任务却要取消/填槽


@dataclass
class TurnPlanValidationResult:
    valid: bool
    reason: ClarifyReason | None = None
