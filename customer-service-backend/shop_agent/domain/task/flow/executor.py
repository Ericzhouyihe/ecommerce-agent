from dataclasses import asdict

from shop_agent.domain.dialogue.messages import BotMessage
from shop_agent.domain.dialogue.state import DialogueState
from shop_agent.domain.task.action.base import ActionResult
from shop_agent.domain.task.action.call import ActionCall
from shop_agent.domain.task.action.runner import ActionRunner
from shop_agent.domain.task.flow.links import (
    ConditionalLink,
    FallbackLink,
    FlowStepLink,
    StaticLink,
)
from shop_agent.domain.task.flow.models import Flow, FlowsList
from shop_agent.domain.task.flow.steps import (
    ActionFlowStep,
    CollectSlotStep,
    EndFlowStep,
    FlowStep,
    StartFlowStep,
)

LISTEN = ActionCall(action_name="action_listen")


class FlowExecutor:
    async def run_task(
        self, state: DialogueState, flows: FlowsList, action_runner: ActionRunner
    ) -> list[BotMessage]:
        messages: list[BotMessage] = []
        while True:
            action_call: ActionCall = self.advance_until_action(state)
            if action_call.action_name == "action_listen":
                break
            else:
                action_result: ActionResult = await action_runner.run(
                    action_call, state
                )
                state.set_slots(action_result.slot_updates)
                messages.extend(action_result.messages)
        return messages

    def advance_until_action(
        self, state: DialogueState, flows: FlowsList
    ) -> ActionCall:
        while True:
            current_task = state.current_task()  # 系统任务优先执行
            if current_task is None:
                return LISTEN

            flow: Flow = flows.get_flow_by_id(current_task.flow_id)
            step: FlowStep = flow.get_step_by_id(current_task.step_id)
            step_result: ActionCall | None = self._run_step(step, state)

            if step_result is not None:
                return step_result

    def _run_step(self, step: FlowStep, state: DialogueState) -> ActionCall | None:
        """运行流程步骤"""
        if isinstance(step, StartFlowStep):
            self._run_start_step(step, state)
        if isinstance(step, CollectSlotStep):
            self._run_collect_step(step, state)
        if isinstance(step, ActionFlowStep):
            self._run_action_step(step, state)
        if isinstance(step, EndFlowStep):
            self._run_end_step(step, state)

    def _run_start_step(
        self, step: StartFlowStep, state: DialogueState
    ) -> ActionCall | None:
        """运行开始步骤"""
        self._advance_to_next_step(step, state)

    def _run_collect_step(
        self, step: CollectSlotStep, state: DialogueState
    ) -> ActionCall | None:
        """运行收集步骤"""

    def _run_action_step(
        self, step: ActionFlowStep, state: DialogueState
    ) -> ActionCall | None:
        # 推进到下一个step
        self._advance_to_next_step(step, state)
        # 封装ActionCall
        action_call: ActionCall = self._build_action_call(step, state)
        return action_call

    def _run_end_step(
        self, step: EndFlowStep, state: DialogueState
    ) -> ActionCall | None:
        """运行结束步骤"""

    def _select_next_step(self, step: FlowStep, state: DialogueState) -> FlowStep:
        """
        选择下一个step_id
        :param step:
        :param state:
        :return: next step id
        """
        links: list[FlowStepLink] = step.next
        for link in links:
            if isinstance(link, StaticLink):
                return link.target
            if isinstance(link, ConditionalLink):
                condition = link.condition
                data = {
                    "slots": state.active_task.slots,
                    "context": asdict(state.current_task()),
                }
                if bool(eval(condition, {}, data)):
                    return link.target
            if isinstance(link, FallbackLink):
                return link.target

    def _advance_to_next_step(self, step: FlowStep, state: DialogueState):
        # 选择下一个step
        next_step_id = self._select_next_step(step, state)
        # 设置state的当前的task的step_id
        state.current_task().step_id = next_step_id

    def _build_action_call(
        self, step: ActionFlowStep, state: DialogueState
    ) -> ActionCall:
        action_name = step.action
        args = step.args
        if isinstance(args, str):
            args = asdict(state.current_task())[args.split(".")[1]]
        return ActionCall(action_name=action_name, action_kwargs=args)


if __name__ == "__main__":
    f = "a>b"
    print(eval(f, {}, {"a": 1, "b": 2}))
