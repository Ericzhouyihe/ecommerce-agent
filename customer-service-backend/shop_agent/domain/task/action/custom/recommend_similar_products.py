from typing import Any

from shop_agent.domain.dialogue.messages import BotMessage
from shop_agent.domain.dialogue.state import DialogueState
from shop_agent.domain.task.action.base import Action, ActionResult
from shop_agent.domain.task.action.custom.shared import fetch_product


class RecommendSimilarProductsAction(Action):
    """相似商品推荐(推荐系统后续接入,当前先给出占位回复)。"""

    name = "action_recommend_similar_products"

    async def run(
        self, state: DialogueState, action_kwargs: dict[str, Any]
    ) -> ActionResult:
        product_id = state.active_task.slots.get("product_id")
        label = product_id or "这件商品"

        payload = await fetch_product(product_id)
        if payload:
            label = str(payload.get("title") or "").strip() or label

        text = (
            f"我已经收到你对\"{label}\"的相似商品推荐需求。"
            "不过当前版本还没有接入正式的推荐系统，稍后可以继续补上这部分能力。"
        )
        return ActionResult(messages=[BotMessage(text=text)])
