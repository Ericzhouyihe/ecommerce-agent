from shop_agent.domain.dialogue.messages import BotMessage
from shop_agent.domain.dialogue.state import DialogueState
from shop_agent.domain.task.action.base import ActionResult
from shop_agent.domain.task.action.runner import ActionCall, ActionRunner
from shop_agent.domain.task.flow.models import FlowsList


class FlowExecutor:
    def run_task(
        self, state: DialogueState, flows: FlowsList, action_runner: ActionRunner
    ) -> list[BotMessage]:
        messages: list[BotMessage] = []
        while True:
            action_call: ActionCall = self.advance_until_action(state)
            if action_call.action_name == "action_listen":
                break
            else:
                action_result: ActionResult = action_runner.run(action_call)
                state.set_slots(action_result.slot_updates)
                messages.extend(action_result.messages)
        return messages

    def advance_until_action(self, state: DialogueState) -> ActionCall:
        pass
