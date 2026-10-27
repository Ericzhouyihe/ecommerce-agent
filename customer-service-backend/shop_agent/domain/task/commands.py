from dataclasses import dataclass
from typing import Any


@dataclass
class Command:
    command: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Command":
        return cls(command=data["command"])


@dataclass
class StartFlowCommand(Command):
    flow: str


@dataclass
class SetSlotsCommand(Command):
    slots: dict[str, Any]


@dataclass
class CancelFlowCommand(Command):
    pass


@dataclass
class ResumeFlowCommand(Command):
    flow: str




def commands_from_json(data: list[dict[str, Any]]) -> list[Command]:
    """从 LLM 输出的 JSON 列表解析为 Command 对象列表。"""
    result: list[Command] = []
    for item in data:
        kind = item.get("command")
        if kind == "start_flow":
            result.append(StartFlowCommand(command=kind, flow=item.get("flow", "")))
        elif kind == "set_slots":
            result.append(SetSlotsCommand(command=kind, slots=item.get("slots", {})))
        elif kind == "cancel_flow":
            result.append(CancelFlowCommand(command=kind))
        elif kind == "resume_flow":
            result.append(ResumeFlowCommand(command=kind, flow=item.get("flow", "")))
    return result

