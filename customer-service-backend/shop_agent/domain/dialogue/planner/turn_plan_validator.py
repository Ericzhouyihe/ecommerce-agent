from shop_agent.domain.dialogue.planner.models import (
    ClarifyReason,
    TurnPlan,
    TurnPlanValidationResult,
)
from shop_agent.domain.dialogue.state import DialogueState
from shop_agent.domain.knowledge.intents import KnowledgeIntent
from shop_agent.domain.task.command.commands import (
    CancelFlowCommand,
    Command,
    ResumeFlowCommand,
    SetSlotsCommand,
    StartFlowCommand,
)
from shop_agent.domain.task.flow.models import FlowsList


class TurnPlanValidator:
    """校验 TurnPlan 是否可执行;不可执行时给出需要澄清的原因。"""

    def validate(
        self,
        turn_plan: TurnPlan,
        state: DialogueState,
        knowledge_intents: dict[str, KnowledgeIntent],
        flows: FlowsList | None = None,
    ) -> TurnPlanValidationResult:
        active_tracks = self._active_tracks(turn_plan)
        if not active_tracks:
            return self._reject(ClarifyReason.MISSING_TRACK)
        if len(active_tracks) > 1:
            return self._reject(ClarifyReason.MULTIPLE_TRACKS)

        track = active_tracks[0]
        if track == "task":
            return self._validate_task(turn_plan, state=state, flows=flows)
        if track == "knowledge":
            return self._validate_knowledge(
                turn_plan, state=state, knowledge_intents=knowledge_intents
            )
        return TurnPlanValidationResult(valid=True)

    @staticmethod
    def _active_tracks(turn_plan: TurnPlan) -> list[str]:
        tracks: list[str] = []
        if turn_plan.task is not None:
            tracks.append("task")
        if turn_plan.knowledge is not None:
            tracks.append("knowledge")
        if turn_plan.chitchat is not None:
            tracks.append("chitchat")
        return tracks

    def _reject(self, reason: ClarifyReason) -> TurnPlanValidationResult:
        return TurnPlanValidationResult(valid=False, reason=reason)

    def _validate_task(
        self,
        turn_plan: TurnPlan,
        state: DialogueState | None = None,
        flows: FlowsList | None = None,
    ) -> TurnPlanValidationResult:
        task_plan = turn_plan.task
        if task_plan is None or not task_plan.commands:
            return self._reject(ClarifyReason.MISSING_TASK_COMMANDS)
        return self._validate_task_commands(
            task_plan.commands,
            state=state,
            flows=flows,
        )

    def _validate_task_commands(
        self,
        commands: list[Command],
        state: DialogueState | None,
        flows: FlowsList | None,
    ) -> TurnPlanValidationResult:
        """拒绝指向不存在流程 / 无任务却取消填槽的指令,避免整轮空回复"""
        if flows is None:
            return TurnPlanValidationResult(valid=True)

        for command in commands:
            if isinstance(command, StartFlowCommand):
                if flows.get_flow_by_id(command.flow) is None:
                    return self._reject(ClarifyReason.INVALID_TASK_TARGET)
            elif isinstance(command, ResumeFlowCommand):
                if flows.get_flow_by_id(command.flow) is None:
                    return self._reject(ClarifyReason.INVALID_TASK_TARGET)
                if state is not None and not any(
                    task.flow_id == command.flow for task in state.paused_tasks
                ):
                    return self._reject(ClarifyReason.INVALID_TASK_TARGET)
            elif isinstance(command, (CancelFlowCommand, SetSlotsCommand)):
                if state is not None and state.active_task is None:
                    return self._reject(ClarifyReason.NO_ACTIVE_TASK)

        return TurnPlanValidationResult(valid=True)

    def _validate_knowledge(
        self,
        turn_plan: TurnPlan,
        state: DialogueState,
        knowledge_intents: dict[str, KnowledgeIntent],
    ) -> TurnPlanValidationResult:
        knowledge_plan = turn_plan.knowledge
        if knowledge_plan is None or not knowledge_plan.intents:
            return self._reject(ClarifyReason.MISSING_KNOWLEDGE_INTENT)

        focused_object = state.focused_object
        for intent_id in knowledge_plan.intents:
            intent_meta = knowledge_intents.get(intent_id)
            if intent_meta is None:
                return self._reject(ClarifyReason.MISSING_KNOWLEDGE_INTENT)
            required_object = intent_meta.requires_object
            if required_object is not None:
                if focused_object is None or focused_object.type != required_object:
                    return self._reject(ClarifyReason.MISSING_FOCUSED_OBJECT)

        return TurnPlanValidationResult(valid=True)
