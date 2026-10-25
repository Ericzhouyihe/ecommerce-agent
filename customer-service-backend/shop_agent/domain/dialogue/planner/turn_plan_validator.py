from shop_agent.domain.dialogue.planner.turn_planner import TurnKind, TurnPlan


class TurnPlanValidator:
    def __init__(self):
        pass

    def validate(self, plan: TurnPlan) -> bool:
        return plan.kind != TurnKind.INVALID


from shop_agent.domain.dialogue.planner.turn_planner import TurnPlan
from shop_agent.domain.dialogue.state import DialogueState


def validate_turn_plan(plan: TurnPlan, state: DialogueState) -> TurnPlan:
    # 第一步先恒等返回。第3步接 flow 时再补:
    #   有 state.active_task 且本句能解析成它正在收集的槽位 → 改判为 TASK
    if plan.kind == TurnKind.TASK and not plan.flow_id:
        plan.kind = TurnKind.INVALID
        plan.reason = "task without flow_id"
    return plan
