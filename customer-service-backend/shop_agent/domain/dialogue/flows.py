from dataclasses import dataclass, field
from enum import Enum


class StepType(Enum):
    START = "start"
    END = "end"
    ACTION = "action"
    COLLECT = "collect"


@dataclass(frozen=True)
class NextRule:  # 条件跳转: cond None 表示 else
    cond: str | None
    target: str


@dataclass(frozen=True)
class StepDefinition:
    id: str
    type: StepType
    next: str | list[NextRule] | None = None
    action: str | None = None  # type == ACTION
    args: dict = field(default_factory=dict)
    slot_name: str | None = None  # type == COLLECT
    response: dict | None = None


@dataclass(frozen=True)
class FlowDefinition:
    flow_id: str
    name: str
    description: str
    steps: dict[str, StepDefinition]  # 用 dict 而非 list,查找 O(1)

    def first_step(self) -> StepDefinition: ...
