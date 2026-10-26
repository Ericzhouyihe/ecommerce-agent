from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from shop_agent.domain.task.flow.links import FlowStepLink, StaticLink, link_from_json


class FlowStepType(str, Enum):
    START = "start"
    ACTION = "action"
    COLLECT = "collect"
    SET_SLOTS = "set_slots"
    END = "end"


@dataclass(slots=True)
class ResponseDefinition:
    mode: str = "static"
    text: str | None = None
    prompt: str | None = None

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> "ResponseDefinition":
        return cls(
            mode=str(data.get("mode", "static")),
            text=None if data.get("text") is None else str(data["text"]),
            prompt=None if data.get("prompt") is None else str(data["prompt"]),
        )


@dataclass(slots=True)
class SlotValidation:
    condition: str | None = None
    failure_response: ResponseDefinition | None = None


@dataclass(slots=True)
class FlowStep:
    id: str
    type: FlowStepType
    next: list[FlowStepLink] = field(default_factory=list)
    description: str = ""

    @staticmethod
    def base_fields(step_data: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": step_data["id"],
            "type": FlowStepType(step_data["type"]),
            "next": load_next_links(raw_next=step_data.get("next")),
            "description": step_data.get("description", ""),
        }


@dataclass(slots=True)
class StartFlowStep(FlowStep):
    @classmethod
    def from_dict(cls, step_data: dict[str, Any]) -> "StartFlowStep":
        return cls(**cls.base_fields(step_data))


@dataclass(slots=True)
class ActionFlowStep(FlowStep):
    type: FlowStepType = FlowStepType.ACTION
    action: str = ""
    args: dict[str, Any] | str = field(default_factory=dict)

    @classmethod
    def from_dict(cls, step_data: dict[str, Any]) -> "ActionFlowStep":
        return cls(
            **cls.base_fields(step_data),
            action=str(step_data.get("action", "")),
            args=step_data.get("args", {}),
        )


@dataclass(slots=True)
class CollectSlotStep(FlowStep):
    type: FlowStepType = FlowStepType.COLLECT
    slot_name: str = ""
    response: ResponseDefinition = field(default_factory=ResponseDefinition)
    validation: SlotValidation | None = None

    @classmethod
    def from_dict(cls, step_data: dict[str, Any]) -> "CollectSlotStep":
        return cls(
            **cls.base_fields(step_data),
            slot_name=str(step_data.get("slot_name", "")),
            response=ResponseDefinition(**(step_data.get("response") or {})),
            validation=(
                SlotValidation(
                    condition=step_data.get("validation").get("condition"),
                    failure_response=ResponseDefinition(
                        **(step_data.get("validation").get("failure_response") or {})
                    ),
                )
                if "validation" in step_data
                else None
            ),
        )


@dataclass(slots=True)
class SetSlotsFlowStep(FlowStep):
    type: FlowStepType = FlowStepType.SET_SLOTS
    slots: list[dict[str, Any]] = field(default_factory=list)

    @classmethod
    def from_dict(cls, step_data: dict[str, Any]) -> "SetSlotsFlowStep":
        return cls(
            **cls.base_fields(step_data),
            slots=list(step_data.get("slots") or []),
        )


@dataclass(slots=True)
class EndFlowStep(FlowStep):
    @classmethod
    def from_dict(cls, step_data: dict[str, Any]) -> "EndFlowStep":
        return cls(**cls.base_fields(step_data))


def step_from_json(step_data: dict[str, Any]) -> FlowStep:
    step_type = FlowStepType(step_data["type"])
    parser = STEP_TYPE_TO_CLASS[step_type]
    return parser(step_data)


STEP_TYPE_TO_CLASS: dict[FlowStepType, Callable[[dict[str, Any]], FlowStep]] = {
    FlowStepType.START: StartFlowStep.from_dict,
    FlowStepType.ACTION: ActionFlowStep.from_dict,
    FlowStepType.COLLECT: CollectSlotStep.from_dict,
    FlowStepType.SET_SLOTS: SetSlotsFlowStep.from_dict,
    FlowStepType.END: EndFlowStep.from_dict,
}


def load_next_links(*, raw_next: Any) -> list[FlowStepLink]:
    if isinstance(raw_next, str):
        return [StaticLink.from_json(raw_next)]

    links: list[FlowStepLink] = []
    for item in raw_next or []:
        links.append(link_from_json(item))
    return links
