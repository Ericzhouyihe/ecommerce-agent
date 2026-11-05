from dataclasses import dataclass, field
from typing import Any


@dataclass
class ActionCall:
    action_name: str
    action_kwargs: dict[str, Any] = field(default_factory=dict)
