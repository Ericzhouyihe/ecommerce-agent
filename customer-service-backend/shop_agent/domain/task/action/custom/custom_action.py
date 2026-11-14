from typing import Any

from shop_agent.domain.dialogue.state import DialogueState
from shop_agent.domain.task.action.base import Action, ActionResult


class CustomAction(Action):
    name = "custom"

    async def run(
        self, state: DialogueState, action_kwargs: dict[str, Any]
    ) -> ActionResult:
        """运行自定义操作"""
        print("Running custom action.")
        return ActionResult()
