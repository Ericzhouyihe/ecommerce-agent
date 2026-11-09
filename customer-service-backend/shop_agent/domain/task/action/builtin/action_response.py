from typing import Any

from jinja2 import Template

from shop_agent.domain.dialogue.messages import BotMessage
from shop_agent.domain.dialogue.state import DialogueState
from shop_agent.domain.task.action.base import Action, ActionResult


class ActionResponse(Action):
    async def run(self, state: DialogueState, action_kwargs: dict[str, Any]) -> ActionResult:
        mode = action_kwargs.get("model", "static")
        if mode == "static":
            text = action_kwargs["text"]
            rendered_text = self._render_text(text, state)
            return ActionResult(messages=[BotMessage(text=rendered_text)])
        elif mode == "repharse":
            text = action_kwargs["text"]

        else:
            pass

    def _render_text(self, text: str, state: DialogueState) -> str:
        """渲染文本, 使用jinja2模板渲染文本"""
        template = Template(text)
        return template.render(
            slots=state.active_task.slots, context=state.active_system_task or state.active_task
        )
