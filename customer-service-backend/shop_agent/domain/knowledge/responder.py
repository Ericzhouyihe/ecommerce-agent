from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

from shop_agent.domain.dialogue.messages import BotMessage, UserMessage
from shop_agent.domain.dialogue.state import Turn
from shop_agent.infrastructure.llm import llm
from shop_agent.domain.knowledge.providers import KnowledgeChunk
from shop_agent.prompts.history_builder import HistoryBuilder
from shop_agent.prompts.loader import load_prompt


class KnowledgeResponder:
    async def respond(
            self,
            user_message: UserMessage,
            recent_turns: list[Turn],
            chunks: list[KnowledgeChunk],
    ) -> list[BotMessage]:
        # 准备提示词上下文
        user_message = HistoryBuilder._render_user_message(user_message)
        history = HistoryBuilder.build(recent_turns)
        knowledge_content = "\n\n".join([chunk.content for chunk in chunks])

        # 构造chain
        prompt_text = load_prompt("knowledge_respond")
        prompt = PromptTemplate.from_template(
            prompt_text,
            template_format="jinja2"
        )
        chain = prompt | llm | StrOutputParser()

        # 运行chain
        response = await chain.ainvoke({
            "user_message": user_message,
            "history": history,
            "knowledge_content": knowledge_content,
        })

        return [BotMessage(text=response)]
