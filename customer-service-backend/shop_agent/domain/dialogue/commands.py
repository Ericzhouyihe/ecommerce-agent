from dataclasses import dataclass, field
from enum import Enum

from shop_agent.domain.dialogue.state import DialogueState


class CommandKind(Enum):
    START_FLOW = "start_flow"
    SET_SLOTS = "set_slots"
    CANCEL_FLOW = "cancel_flow"
    RESUME_FLOW = "resume_task"


@dataclass(frozen=True)
class Command:
    kind: CommandKind
    flow_id: str | None = None
    slots: dict = field(default_factory=dict)


class CommandProcessor:
    def apply(self, state: DialogueState, commands: list[Command]) -> None: ...
