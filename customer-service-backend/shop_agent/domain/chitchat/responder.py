import asyncio

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

from shop_agent.domain.dialogue.messages import UserMessage, BotMessage, MessageType
from shop_agent.domain.dialogue.state import Turn
from shop_agent.infrastructure.llm import llm
from shop_agent.prompts.history_builder import HistoryBuilder
from shop_agent.prompts.loader import load_prompt


class ChitchatResponder:

    async def respond(
            self,
            user_message: UserMessage,
            recent_turns: list[Turn],
    ) -> list[BotMessage]:
        user_message = HistoryBuilder._render_user_message(user_message)
        history = HistoryBuilder.build(recent_turns)

        prompt_text = load_prompt("chitchat_respond")
        prompt = PromptTemplate.from_template(
            prompt_text,
            template_format="jinja2"
        )
        chain = prompt | llm | StrOutputParser()
        response = await chain.ainvoke({
            "user_message": user_message,
            "history": history,
        })
        return [BotMessage(text=response)]


if __name__ == '__main__':
    chitchat_responder = ChitchatResponder()


    async def test():
        response = await chitchat_responder.respond(
            user_message=UserMessage(
                sender_id="u1001",
                message_id="m1001",
                type=MessageType.TEXT,
                text="你好"
            ),
            recent_turns=[]
        )
        print(response)


    asyncio.run(test())
