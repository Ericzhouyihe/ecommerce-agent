from typing import Any

from shop_agent.domain.dialogue.state import DialogueState
from shop_agent.domain.task.action.base import Action, ActionResult


class ActionResponse(Action):
    async def run(self, state: DialogueState, action_kwargs: dict[str, Any]) -> ActionResult:
        pass
