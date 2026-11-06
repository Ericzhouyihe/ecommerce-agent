from dataclasses import dataclass, field
from typing import Any

from shop_agent.domain.dialogue.state import DialogueState
from shop_agent.domain.task.action.base import ActionResult
from shop_agent.domain.task.action.registry import ActionRegistry


@dataclass
class ActionCall:
    action_name: str
    action_kwargs: dict[str, Any] = field(default_factory=dict)


class ActionRunner:
    """执行流程执行器请求的操作"""

    def __init__(self, registry: ActionRegistry) -> None:
        self.registry = registry

    async def run(self, action_call: ActionCall, state: DialogueState) -> ActionResult:
        action_name = action_call.action_name
        action = self.registry.get(action_name)
        return await action.run(state, action_call.action_kwargs)
