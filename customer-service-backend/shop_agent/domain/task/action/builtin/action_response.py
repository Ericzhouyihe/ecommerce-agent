from typing import Any

from jinja2 import Template
from langchain import PromptTemplate, StrOutputParser

from shop_agent.domain.dialogue.messages import BotMessage
from shop_agent.domain.dialogue.state import DialogueState
from shop_agent.domain.task.action.base import Action, ActionResult
from shop_agent.infrastructure import llm
from shop_agent.prompts.history_builder import HistoryBuilder


class ActionResponse(Action):
    async def run(
        self, state: DialogueState, action_kwargs: dict[str, Any]
    ) -> ActionResult:
        mode = action_kwargs.get("model", "static")
        if mode == "static":
            text = action_kwargs["text"]
            rendered_text = self._render_text(text, state)
            return ActionResult(messages=[BotMessage(text=rendered_text)])
        elif mode == "repharse":
            text = action_kwargs["text"]
            rendered_text = self._render_text(text, state)
            prompt_text = action_kwargs["prompt"]
            message = await self._call_llm(rendered_text, prompt_text, state)
            return ActionResult(messages=[BotMessage(text=message)])
        else:
            pass

    def _render_text(self, text: str, state: DialogueState) -> str:
        """渲染文本, 使用jinja2模板渲染文本"""
        template = Template(text)
        return template.render(
            slots=state.active_task.slots,
            context=state.active_system_task or state.active_task,
        )

    async def _call_llm(
        self, rendered_text: str, prompt_text: str, state: DialogueState
    ) -> str:
        """调用模型, 返回模型回复"""
        prompt = PromptTemplate.from_template(prompt_text, template_type="jinja2")

        output_parser = StrOutputParser()
        chain = prompt | llm | output_parser

        response = await chain.ainvoke(
            {
                "history": HistoryBuilder.build(state.turns),
                "user_message": "",
                "current_response": rendered_text,
            }
        )
        return response
