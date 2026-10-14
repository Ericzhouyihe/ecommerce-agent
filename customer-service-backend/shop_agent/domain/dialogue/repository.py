from abc import ABC, abstractmethod

from shop_agent.domain.dialogue.state import DialogueState


class DialogueStateRepository(ABC):
    """DialogueState 聚合根的持久化契约;实现放 infrastructure"""

    @abstractmethod
    async def load_state(self, sender_id: str) -> DialogueState:
        """加载该用户的对话状态;不存在则返回全新实例。

        契约:不得返回 None、不得抛"未找到"异常——
        新用户和新会话对调用方而言无差别。
        """

    @abstractmethod
    async def save_state(self, sender_id: str, state: DialogueState) -> None:
        """保存整个聚合;存在则整体覆盖。

        契约:调用方不区分"新建还是更新"(upsert 语义)。
        """
