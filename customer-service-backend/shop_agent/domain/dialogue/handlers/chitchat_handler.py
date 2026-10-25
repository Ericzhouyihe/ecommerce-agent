from shop_agent.domain.dialogue.messages import BotMessage
from shop_agent.domain.dialogue.sessions import Session


async def handle_chitchat(text: str, session: Session) -> BotMessage:
    return BotMessage(text="你好呀～有什么可以帮你的吗？")
