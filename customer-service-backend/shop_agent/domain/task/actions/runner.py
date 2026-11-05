from shop_agent.domain.dialogue.state import DialogueState
from shop_agent.domain.task.actions.base import ActionResult
from shop_agent.domain.task.actions.call import ActionCall
from shop_agent.domain.task.actions.registry import ActionRegistry


class ActionRunner:
    """Execute actions requested by the flow executor."""

    def __init__(
        self,
        registry: ActionRegistry,
    ) -> None:
        self.registry = registry

    async def run(
        self,
        action_call: ActionCall,
        state: DialogueState,
    ) -> ActionResult:
        action_name = action_call.action_name
        action = self.registry.get(action_name)
        return await action.run(state, action_call.action_kwargs)
