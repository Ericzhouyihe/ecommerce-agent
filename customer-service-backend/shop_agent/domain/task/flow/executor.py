from dataclasses import dataclass

from shop_agent.domain.dialogue.messages import BotMessage
from shop_agent.domain.task.contexts import TaskContext
from shop_agent.domain.task.flow.models import Flow


@dataclass
class FlowRunResult:
    messages: list[BotMessage]
    task: TaskContext | None  # None 表示流程结束


async def run_flow(
    flow: Flow,
    task: TaskContext,
    user_text: str | None,
) -> FlowRunResult:
    """
    两种情况:
      A. task.step_id 为 None → 从头开始(start)
      B. task.step_id 有值   → 说明上一轮停在 collect,把 user_text 写入槽位后继续
    """
    raise NotImplementedError("FlowExecutor 待实现")
