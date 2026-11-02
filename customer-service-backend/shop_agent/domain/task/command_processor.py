from shop_agent.domain.dialogue.state import DialogueState
from shop_agent.domain.task.commands import (
    CancelFlowCommand,
    Command,
    ResumeFlowCommand,
    SetSlotsCommand,
    StartFlowCommand,
)
from shop_agent.domain.task.contexts import (
    InterruptedSystemContext,
    StartedSystemContext,
    TaskContext,
)
from shop_agent.domain.task.flow.models import Flow, FlowsList


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

    def _handle_start_flow(
        self, command: StartFlowCommand, state: DialogueState, flows: FlowsList
    ) -> None:
        # 清理清理系统任务的上下文
        state.end_system_task()
        # 获取目标flow
        target_flow: Flow = flows.get_flow_by_id(command.flow)

        # 判断当前是否有正在运行的flow
        if state.active_system_flow is not None:
            # 挂起旧任务
            state.interrupt_active_task()

            # 启动新任务
            state.start_task(
                task_context=TaskContext(
                    flow_id=target_flow.id, step_id=target_flow.start_step().id
                )
            )

            # 启动系统任务
            state.start_system_task(
                system_context=InterruptedSystemContext(
                    flow_id="system_task_started",
                    step_id=flows.get_flow_by_id("system_task_started").start_step().id,
                    interrupted_flow_id=target_flow.id,
                    interrupted_flow_name=target_flow.name,
                    started_flow_id=state.active_system_flow.flow_id,
                    started_flow_name=state.active_system_flow.flow_name,
                )
            )

            # 通知用户新任务已启动
            state.add_message("system", "new_task_started")
            return
        else:
            state.start_task(
                task_context=TaskContext(
                    flow_id=target_flow.id, step_id=target_flow.start_step().id
                )
            )

            state.start_system_task(
                system_context=StartedSystemContext(
                    flow_id="system_task_started",
                    step_id=flows.get_flow_by_id("system_task_started").start_step().id,
                    started_flow_id=target_flow.id,
                    started_flow_name=target_flow.name,
                )
            )

    def _handle_set_slots(self, command: SetSlotsCommand, state: DialogueState):
        pass

    def _handle_cancel_flow(self, state: DialogueState, flows: FlowsList):
        pass

    def _handle_resume_flow(
        self, command: ResumeFlowCommand, state: DialogueState, flows: FlowsList
    ):
        pass
