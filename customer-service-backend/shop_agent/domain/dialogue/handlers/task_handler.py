from pathlib import Path

from shop_agent.domain.dialogue.messages import BotMessage
from shop_agent.domain.dialogue.planner.turn_planner import TurnPlan
from shop_agent.domain.dialogue.state import DialogueState
from shop_agent.domain.task.contexts import TaskContext
from shop_agent.domain.task.flow.executor import run_flow
from shop_agent.domain.task.flow.loader import FlowLoader

# TODO: 通过依赖注入传入，不要模块级全局
_loader = FlowLoader()
_project_root = Path(__file__).parents[4]
_flows_list = _loader.load_all(
    _project_root / "flow_config" / "system_flows.yml",
    _project_root / "flow_config" / "user_flows.yml",
)


async def handle_task(plan: TurnPlan, state: DialogueState) -> BotMessage:
    flow = _flows_list.flow_by_id(plan.flow_id or "")
    if flow is None:
        return BotMessage(text="抱歉，这个功能暂不可用。")

    task = state.active_task or TaskContext(flow_id=flow.id)
    result = await run_flow(flow, task, plan.user_text)

    state.active_task = result.task  # None 表示流程结束，自动清空
    return result.messages
