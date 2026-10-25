from dataclasses import dataclass, field
from enum import Enum


class TurnKind(Enum):
    CHITCHAT = "chitchat"  # 闲聊
    KNOWLEDGE = "knowledge"  # 知识问答
    TASK = "task"  # 业务任务(要推进 flow)
    INVALID = "invalid"  # 听不懂 / 无法处理


@dataclass
class TurnPlan:
    kind: TurnKind = TurnKind.INVALID
    flow_id: str | None = None  # kind == TASK 时必填
    slots: dict = field(default_factory=dict)  # 本轮抽取到的槽位
    reason: str | None = None  # 为什么判定成 INVALID,便于调试


from shop_agent.domain.dialogue.planner.turn_planner import TurnKind
from shop_agent.domain.dialogue.sessions import Session

TASK_KEYWORDS = {
    "order_status_query": ["查订单", "订单状态", "订单怎么样"],
}
CHITCHAT_KEYWORDS = ["你好", "在吗", "谢谢", "哈哈"]


async def plan_turn(text: str, session: Session) -> TurnPlan:
    # 规则版：第5步再换成 LLM 意图分类
    for flow_id, keywords in TASK_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            return TurnPlan(kind=TurnKind.TASK, flow_id=flow_id)

    if any(kw in text for kw in CHITCHAT_KEYWORDS):
        return TurnPlan(kind=TurnKind.CHITCHAT)

    return TurnPlan(kind=TurnKind.INVALID, reason="no keyword matched")
