from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from shop_agent.domain.dialogue.flow.links import FlowStepLink, StaticLink, link_from_json


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
            text=data.get("text"),
            prompt=data.get("prompt"),
        )


@dataclass(slots=True)
class SlotValidation:
    condition: str | None = None
    failure_response: ResponseDefinition | None = None

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> "SlotValidation":
        raw_failure = data.get("failure_response")
        return cls(
            condition=data.get("condition"),
            failure_response=ResponseDefinition.from_json(raw_failure) if raw_failure else None,
        )


@dataclass(slots=True)
class FlowStep:
    id: str
    type: FlowStepType
    next: list[FlowStepLink] = field(default_factory=list)
    description: str = ""

    @classmethod
    def from_dict(cls, step_data: dict[str, Any]) -> "FlowStep":
        step_type = step_data["type"]
        clz = STEP_TYPE_TO_CLASS[step_type]
        return cls(**load_base_step_fields(step_data))


@dataclass(slots=True)
class StartFlowStep(FlowStep):
    pass


@dataclass(slots=True)
class ActionFlowStep(FlowStep):
    type: FlowStepType = FlowStepType.ACTION
    action: str = ""
    args: dict[str, Any] | str = field(default_factory=dict)

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> "ActionFlowStep":
        return cls(
            **load_base_step_fields(data),
            action=str(data.get("action", "")),
            args=data.get("args", {}),
        )


@dataclass(slots=True)
class CollectSlotStep(FlowStep):
    type: FlowStepType = FlowStepType.COLLECT
    slot_name: str = ""
    response: ResponseDefinition = field(default_factory=ResponseDefinition)
    validation: SlotValidation | None = None

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> "CollectSlotStep":
        raw_response = data.get("response") or {}
        raw_validation = data.get("validation")
        return cls(
            **load_base_step_fields(data),
            slot_name=str(data.get("slot_name", "")),
            response=ResponseDefinition.from_json(raw_response),
            validation=SlotValidation.from_json(raw_validation) if raw_validation else None,
        )


@dataclass(slots=True)
class SetSlotsFlowStep(FlowStep):
    type: FlowStepType = FlowStepType.SET_SLOTS
    slots: list[dict[str, Any]] = field(default_factory=list)

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> "SetSlotsFlowStep":
        return cls(
            **load_base_step_fields(data),
            slots=list(data.get("slots") or []),
        )


@dataclass(slots=True)
class EndFlowStep(FlowStep):
    pass


def step_from_json(data: dict[str, Any]) -> FlowStep:
    step_type = FlowStepType(data["type"])
    parser = STEP_TYPE_TO_CLASS[step_type]
    return parser(data)


def load_base_step_fields(data: dict[str, Any]) -> dict[str, Any]:
    step_type = FlowStepType(data["type"])
    return {
        "id": str(data["id"]),
        "type": step_type,
        "next": load_next_links(raw_next=data.get("next")),
        "description": str(data.get("description", "")),
    }


STEP_TYPE_TO_CLASS: dict[FlowStepType, Callable[[dict[str, Any]], FlowStep]] = {
    FlowStepType.START: StartFlowStep.from_json,
    FlowStepType.ACTION: ActionFlowStep.from_json,
    FlowStepType.COLLECT: CollectSlotStep.from_json,
    FlowStepType.SET_SLOTS: SetSlotsFlowStep.from_json,
    FlowStepType.END: EndFlowStep.from_json,
}


def load_next_links(
    *,
    raw_next: Any,
) -> list[FlowStepLink]:
    if isinstance(raw_next, str):
        return [StaticLink.from_json(raw_next)]

    links: list[FlowStepLink] = []
    for item in raw_next or []:
        links.append(link_from_json(item))
    return links
