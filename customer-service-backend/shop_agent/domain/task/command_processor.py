from shop_agent.domain.task.commands import (
    CancelFlowCommand,
    Command,
    ResumeFlowCommand,
    SetSlotsCommand,
    StartFlowCommand,
)
from shop_agent.domain.task.contexts import TaskContext
from shop_agent.domain.task.flow.models import FlowsList


class CommandProcessor:
    """把 Command 应用到 DialogueState 上。

    职责边界:
      - 只修改 active_task / paused_tasks / active_system_flow 三类状态
      - 不读数据库、不调 LLM、不执行 action
      - 流程推进交给 FlowExecutor,由 TaskHandler 串联
    """

    def apply(self, state, commands: list[Command], flows: FlowsList) -> None:
        for command in commands:
            self._apply(command, state, flows)

    def _apply(self, command: Command, state, flows: FlowsList) -> None:
        if isinstance(command, StartFlowCommand):
            self._handle_start_flow(command, state, flows)
        elif isinstance(command, SetSlotsCommand):
            self._handle_set_slots(command, state)
        elif isinstance(command, CancelFlowCommand):
            self._handle_cancel_flow(state)
        elif isinstance(command, ResumeFlowCommand):
            self._handle_resume_flow(command, state)

    def _handle_start_flow(self, command: StartFlowCommand, state, flows: FlowsList) -> None:
        flow = flows.flow_by_id(command.flow)
        if flow is None:
            return
        start = flow.start_step()
        if start is None:
            return

        # 已有同名任务在跑 → 不重复启动
        if state.active_task and state.active_task.flow_id == command.flow:
            return

        # 有其他任务在跑 → 压栈暂停
        if state.active_task:
            state.paused_tasks.append(state.active_task)

        state.active_task = TaskContext(flow_id=command.flow, step_id=start.id)

    def _handle_set_slots(self, command: SetSlotsCommand, state) -> None:
        if state.active_task is None:
            return
        state.active_task.slots.update(command.slots)

    def _handle_cancel_flow(self, state) -> None:
        state.active_task = None

    def _handle_resume_flow(self, command: ResumeFlowCommand, state) -> None:
        for i, task in enumerate(state.paused_tasks):
            if task.flow_id == command.flow:
                state.paused_tasks.pop(i)
                # 当前任务压栈，恢复目标任务
                if state.active_task:
                    state.paused_tasks.append(state.active_task)
                state.active_task = task
                return
