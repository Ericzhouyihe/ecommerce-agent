from typing import Any

from shop_agent.domain.dialogue.state import DialogueState
from shop_agent.domain.task.action.base import Action, ActionResult


class ActionListen(Action):
    def run(self, state: DialogueState, action_kwargs: dict[str, Any]) -> ActionResult:
        pass
