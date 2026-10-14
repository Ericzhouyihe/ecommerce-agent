from shop_agent.domain.dialogue.message import ProcessResult, UserMessage
from shop_agent.domain.dialogue.state import DialogueState


class DialogueEngine:
    def process_message(
        self, dialogue_state: DialogueState, user_message: UserMessage
    ) -> ProcessResult:
        pass
