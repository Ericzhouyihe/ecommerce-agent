import json

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

from shop_agent.domain.dialogue.messages import BotMessage
from shop_agent.domain.dialogue.planner.models import ClarifyReason
from shop_agent.domain.dialogue.state import DialogueState
from shop_agent.infrastructure.llm import llm
from shop_agent.prompts.history_builder import HistoryBuilder
from shop_agent.prompts.loader import load_prompt


class ClarifyResponder:
    """把校验失败的澄清原因改写成一句自然的追问。"""

    async def respond(
        self, state: DialogueState, reason: ClarifyReason
    ) -> list[BotMessage]:
        message = state.pending_turn.user_message
        clarify_message = self.build_clarify_message(reason=reason, state=state)
        prompt_text = load_prompt("clarify_respond")
        prompt = PromptTemplate.from_template(prompt_text, template_format="jinja2")
        chain = prompt | llm | StrOutputParser()
        rewritten = await chain.ainvoke(
            {
                "reason": reason.value,
                "clarify_message": clarify_message,
                "focused_object": json.dumps(
                    state.focused_object.to_dict(), ensure_ascii=False
                )
                if state.focused_object
                else "",
                "history": HistoryBuilder.build(state.current_session().turns),
                "user_message": HistoryBuilder._render_user_message(message),
            }
        )
        return [BotMessage(text=rewritten)]

    def build_clarify_message(
        self, reason: ClarifyReason, state: DialogueState
    ) -> str:
        if reason is ClarifyReason.MULTIPLE_TRACKS:
            return "你这次同时提到了多个方向。我们先处理一个，你想先办业务还是先咨询信息呢？"

        if reason is ClarifyReason.MISSING_FOCUSED_OBJECT:
            return "请先发送你想咨询的对象，我再继续帮你看。"

        if reason is ClarifyReason.MISSING_KNOWLEDGE_INTENT:
            return "你是想了解商品信息、订单信息，还是售后配送规则呢？"

        if reason is ClarifyReason.MISSING_TRACK:
            return "你是想先处理业务问题，还是先咨询信息呢？"

        if reason is ClarifyReason.MISSING_TASK_COMMANDS:
            return "你这次是想办理什么业务呢？比如查订单、查物流，或者申请退款。"

        if reason is ClarifyReason.INVALID_TASK_TARGET:
            return "这个业务我这边暂时办不了，你可以试试查订单状态、查物流，或者申请退款。"

        if reason is ClarifyReason.NO_ACTIVE_TASK:
            return "现在我们还没有正在进行的事情，你想先办哪一件呢？比如查订单、查物流，或者申请退款。"

        if reason is ClarifyReason.OBJECT_REQUIRES_INTENT:
            focused_object = state.focused_object
            if focused_object is not None and focused_object.type == "order":
                return "我已经收到这个订单了。你想查订单状态、查物流，还是申请退款呢？"
            if focused_object is not None and focused_object.type == "product":
                return "我已经收到这个商品了。你想了解它的商品信息、发货情况，还是售后相关信息呢？"

        return "我还需要再确认一下你的意思，你可以换个更具体的说法告诉我。"
