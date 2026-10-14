from shop_agent.domain.dialogue.engine import DialogueEngine
from shop_agent.domain.dialogue.messages import ProcessResult, UserMessage
from shop_agent.domain.dialogue.repository import DialogueStateRepository
from shop_agent.domain.dialogue.state import DialogueState


class DialogueService:
    def __init__(
        self, dialogue_state_repository: DialogueStateRepository, dialogue_engine: DialogueEngine
    ):
        self.dialogue_state_repository = dialogue_state_repository
        self.dialogue_engine = dialogue_engine

    async def process_message(self, user_message: UserMessage) -> ProcessResult:
        # 1. 通过 dialogue_state_repository 根据 sender_id 加载用户对话状态
        dialogue_state: DialogueState = await self.dialogue_state_repository.load_state(
            user_message.sender_id
        )

        # 2. 调用 dialogue_engine 根据对话状态处理用户消息
        process_result: ProcessResult = await self.dialogue_engine.process_message(
            dialogue_state, user_message
        )

        # 3. 通过 dialogue_state_repository 保存最新的对话状态
        await self.dialogue_state_repository.save_state(user_message.sender_id, dialogue_state)

        # 4. 返回本轮处理结果
        return process_result
