from dataclasses import dataclass, field
from typing import Any


@dataclass
class TaskContext:
    flow_id: str
    step_id: str | None = None
    slots: dict = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {"flow_id": self.flow_id, "step_id": self.step_id, "slots": self.slots}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TaskContext":
        return cls(
            flow_id=data["flow_id"], step_id=data.get("step_id"), slots=data.get("slots", {})
        )


@dataclass
class SystemContext:
    flow_id: str
    step_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {"flow_id": self.flow_id, "step_id": self.step_id}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SystemContext":
        return cls(flow_id=data["flow_id"], step_id=data.get("step_id"))


@dataclass
class StartedSystemContext(SystemContext):
    started_flow_id: str = ""
    started_flow_name: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            **super().to_dict(),
            "started_flow_id": self.started_flow_id,
            "started_flow_name": self.started_flow_name,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "StartedSystemContext":
        return cls(
            flow_id=data["flow_id"],
            step_id=data.get("step_id"),
            started_flow_id=data.get("started_flow_id", ""),
            started_flow_name=data.get("started_flow_name", ""),
        )


@dataclass
class InterruptedSystemContext(SystemContext):
    interrupted_flow_id: str = ""
    interrupted_flow_name: str = ""
    started_flow_id: str = ""
    started_flow_name: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            **super().to_dict(),
            "interrupted_flow_id": self.interrupted_flow_id,
            "interrupted_flow_name": self.interrupted_flow_name,
            "started_flow_id": self.started_flow_id,
            "started_flow_name": self.started_flow_name,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "InterruptedSystemContext":
        return cls(
            flow_id=data["flow_id"],
            step_id=data.get("step_id"),
            interrupted_flow_id=data.get("interrupted_flow_id", ""),
            interrupted_flow_name=data.get("interrupted_flow_name", ""),
            started_flow_id=data.get("started_flow_id", ""),
            started_flow_name=data.get("started_flow_name", ""),
        )


# flow_id 本身就能区分是哪个 system flow,借它做反序列化的派发键
SYSTEM_CONTEXT_TYPES: dict[str, type[SystemContext]] = {
    "system_task_started": StartedSystemContext,
    "system_task_interrupted": InterruptedSystemContext,
}


def system_context_from_dict(data: dict[str, Any]) -> SystemContext:
    """按 flow_id 还原成具体子类,避免子类字段在落库后丢失。"""
    context_type = SYSTEM_CONTEXT_TYPES.get(data.get("flow_id", ""), SystemContext)
    return context_type.from_dict(data)
