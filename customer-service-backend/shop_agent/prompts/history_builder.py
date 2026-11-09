from shop_agent.domain.dialogue.messages import (
    BotMessage,
    MessageObject,
    MessageType,
    UserMessage,
)
from shop_agent.domain.dialogue.sessions import Turn


class HistoryBuilder:
    @staticmethod
    def build(turns: list[Turn]) -> str:
        """构建历史记录
        :return:
        USER: {user_message}
        BOT: {bot_response}
        BOT: {bot_response}
        USER: {user_message}
        BOT: {bot_response}
        """
        messages: list[str] = []
        for turn in turns:
            # 用户消息
            user_message = turn.user_message
            render_user_message = HistoryBuilder._render_user_message(user_message)
            messages.append(f"USER: {render_user_message}")

            # 机器人消息
            for bot_message in turn.bot_messages:
                render_bot_message = HistoryBuilder._render_bot_message(bot_message)
                messages.append(f"BOT: {render_bot_message}")
        return "\n".join(messages)

    @staticmethod
    def _render_text(text: str) -> str:
        return text.strip()

    @staticmethod
    def _render_object(object: MessageObject) -> str:
        # [订单对象 id=A1001, title='手机', attr1=value1, attr2=value2, attr3=value3]
        label = "订单对象" if object.type == "order" else "商品对象"
        id = object.id
        title = object.title
        attributes = object.attributes
        attr_str = ", ".join([f"{key}={value}" for key, value in attributes.items()])
        return f"[{label} id={id}, title={title}, {attr_str}]"

    @staticmethod
    def _render_user_message(user_message: UserMessage) -> str:
        if user_message.type == MessageType.TEXT:
            return HistoryBuilder._render_text(user_message.text)
        else:
            return HistoryBuilder._render_object(user_message.object)

    @staticmethod
    def _render_bot_message(bot_message: BotMessage) -> str:
        if bot_message.text:
            return HistoryBuilder._render_text(bot_message.text)
        else:
            return HistoryBuilder._render_object(bot_message.object)
