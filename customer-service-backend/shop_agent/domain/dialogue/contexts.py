from dataclasses import dataclass
from typing import Any


@dataclass
class SystemContext:
    flow_id: str
    step_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {"flow_id": self.flow_id, "step_id": self.step_id}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SystemContext":
        return cls(flow_id=data["flow_id"], step_id=data.get("step_id"))
