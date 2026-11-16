from typing import Any

from shop_agent.domain.dialogue.state import DialogueState
from shop_agent.domain.task.action.base import Action, ActionResult


class ActionListen(Action):
    """占位动作:流程走到这里意味着"等用户说话",由执行器终止循环。"""

    name = "action_listen"

    async def run(
        self, state: DialogueState, action_kwargs: dict[str, Any]
    ) -> ActionResult:
        return ActionResult()
