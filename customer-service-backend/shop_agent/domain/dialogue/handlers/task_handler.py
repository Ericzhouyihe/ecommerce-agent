from shop_agent.domain.dialogue.contexts import TaskContext
from shop_agent.domain.dialogue.flow.executor import run_flow
from shop_agent.domain.dialogue.messages import BotMessage
from shop_agent.domain.dialogue.planner.turn_planner import TurnPlan
from shop_agent.domain.dialogue.state import DialogueState
from shop_agent.infrastructure.flow_loader import get_flows


async def handle_task(plan: TurnPlan, state: DialogueState) -> BotMessage:
    flows = get_flows()
    flow = flows.get(plan.flow_id or "")
    if flow is None:
        return BotMessage(text="抱歉，这个功能暂不可用。")

    task = state.active_task or TaskContext(flow_id=flow.flow_id)
    result = await run_flow(flow, task, plan.user_text)

    state.active_task = result.task  # None 表示流程结束，自动清空
    return result.messages
