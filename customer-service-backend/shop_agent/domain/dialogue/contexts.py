from dataclasses import dataclass, field


@dataclass
class TaskContext:
    flow_id: str
    step_id: str | None = None
    slots: dict = field(default_factory=dict)


@dataclass
class SystemContext:
    flow_id: str
    step_id: str | None = None
