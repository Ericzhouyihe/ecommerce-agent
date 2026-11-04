from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class TaskContext:
    """业务任务执行快照（对应用户发起的对话流程）。"""

    flow_id: str
    step_id: str | None = None
    slots: dict = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {"flow_id": self.flow_id, "step_id": self.step_id, "slots": self.slots}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TaskContext":
        return cls(flow_id=data["flow_id"], step_id=data["step_id"], slots=data["slots"])


@dataclass(slots=True)
class SystemContext:
    flow_id: str
    step_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SystemContext":
        clz = FLOW_ID_TO_CONTEXT_CLASS[data["flow_id"]]
        return clz(**data)


@dataclass(slots=True)
class StartedSystemContext(SystemContext):
    started_flow_id: str = ""
    started_flow_name: str = ""


@dataclass(slots=True)
class InterruptedSystemContext(SystemContext):
    interrupted_flow_id: str = ""
    interrupted_flow_name: str = ""
    started_flow_id: str = ""
    started_flow_name: str = ""


@dataclass
class CanceledSystemContext(SystemContext):
    canceled_flow_id: str = ""
    canceled_flow_name: str = ""


@dataclass(slots=True)
class ResumedSystemContext(SystemContext):
    resumed_flow_id: str = ""
    resumed_flow_name: str = ""


@dataclass(slots=True)
class CollectSystemContext(SystemContext):
    pass


@dataclass(slots=True)
class CannotHandleSystemContext(SystemContext):
    pass


@dataclass(slots=True)
class CompletedSystemContext(SystemContext):
    pass


FLOW_ID_TO_CONTEXT_CLASS: dict[str, type] = {
    "started": StartedSystemContext,
    "interrupted": InterruptedSystemContext,
    "collect": CollectSystemContext,
    "resumed": ResumedSystemContext,
    "canceled": CanceledSystemContext,
    "cannot_handle": CannotHandleSystemContext,
    "completed": CompletedSystemContext,
}
