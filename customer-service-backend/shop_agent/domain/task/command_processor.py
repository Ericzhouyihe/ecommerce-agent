from shop_agent.domain.dialogue.state import DialogueState
from shop_agent.domain.task.commands import (
    CancelFlowCommand,
    Command,
    ResumeFlowCommand,
    SetSlotsCommand,
    StartFlowCommand,
)
from shop_agent.domain.task.contexts import (
    CanceledSystemContext,
    InterruptedSystemContext,
    ResumedSystemContext,
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

    def _handle_start_flow(self, command: StartFlowCommand, state: DialogueState, flows: FlowsList):
        # 清理清理系统任务的上下文
        state.end_system_task()
        # 获取目标flow
        target_flow: Flow = flows.get_flow_by_id(flow_id=command.flow)

        active_task = state.active_task
        # 判断当前是否有正在运行的flow
        if active_task is not None:
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
                    flow_id="system_task_interrupted",
                    step_id=flows.get_flow_by_id(flow_id="system_task_interrupted").start_step().id,
                    interrupted_flow_id=active_task.flow_id,
                    interrupted_flow_name=flows.get_flow_by_id(flow_id=active_task.flow_id).name,
                    started_flow_id=target_flow.id,
                    started_flow_name=target_flow.name,
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
                    step_id=flows.get_flow_by_id(flow_id="system_task_started").start_step().id,
                    started_flow_id=target_flow.id,
                    started_flow_name=target_flow.name,
                )
            )

    def _handle_set_slots(self, command: SetSlotsCommand, state: DialogueState):
        if state.active_task:
            state.set_slots(slots=command.slots)

    def _handle_cancel_flow(self, state: DialogueState, flows: FlowsList):
        active_task = state.active_task
        target_flow = flows.get_flow_by_id(flow_id=active_task.flow_id)

        # 取消当前task
        state.cancel_active_task()

        # 启动system_task_canceled
        state.start_system_task(
            system_context=CanceledSystemContext(
                flow_id="system_task_canceled",
                step_id=flows.get_flow_by_id(flow_id="system_task_canceled").start_step().id,
                canceled_flow_id=target_flow.id,
                canceled_flow_name=target_flow.name,
            )
        )

    def _handle_resume_flow(
        self, command: ResumeFlowCommand, state: DialogueState, flows: FlowsList
    ):
        target_flow: Flow = flows.get_flow_by_id(flow_id=command.flow)
        if target_flow is None:
            return

        active_task = state.active_task

        if active_task:
            if target_flow.id == active_task.flow_id:
                return

            # 暂停当前任务
            state.interrupt_active_task()
            # 恢复目标任务
            state.resume_task(target_flow.id)
            # 启动system_task_interrupted
            state.start_system_task(
                InterruptedSystemContext(
                    flow_id="system_task_interrupted",
                    step_id=flows.get_flow_by_id("system_task_interrupted").start_step().id,
                    interrupted_flow_id=active_task.flow_id,
                    interrupted_flow_name=flows.get_flow_by_id(active_task.flow_id).name,
                    started_flow_id=target_flow.id,
                    started_flow_name=target_flow.name,
                )
            )

        else:
            # 恢复目标任务
            state.resume_task(task_context=target_flow.id)
            # 启动system_task_resumed
            state.start_system_task(
                ResumedSystemContext(
                    flow_id="system_task_resumed",
                    step_id=flows.get_flow_by_id("system_task_resumed").start_step().id,
                    resumed_flow_id=target_flow.id,
                    resumed_flow_name=target_flow.name,
                )
            )
