import time
import uuid

from shop_agent.domain.dialogue.messages import BotMessage, MessageType, ProcessResult, UserMessage
from shop_agent.domain.dialogue.sessions import Session, Turn
from shop_agent.domain.dialogue.state import DialogueState

SESSION_TIMEOUT_SECONDS = 60 * 30


class DialogueEngine:
    async def process_message(
        self, dialogue_state: DialogueState, user_message: UserMessage
    ) -> ProcessResult:
        session = self._prepare_session(dialogue_state)

        # 1.创建本轮 Turn(先挂成 pending,提交时才转正)
        turn = Turn(
            turn_id=str(uuid.uuid4()),
            input_message=user_message,
            assistant_messages=[],
        )
        dialogue_state.pending_turn = turn

        # 2.处理本轮消息
        if user_message.type == MessageType.OBJECT:
            replies = [BotMessage(text="收到对象消息(待实现)")]
        else:
            replies = [BotMessage(text="收到文本消息(待实现)")]

        turn.assistant_messages.extend(replies)

        # 3.提交本轮:写进 session,清空 pending_turn
        session.turns.append(turn)
        session.last_activity_at = time.time()
        dialogue_state.pending_turn = None

        return ProcessResult(
            sender_id=user_message.sender_id,
            message_id=user_message.message_id,
            messages=replies,
        )

    def _prepare_session(self, state: DialogueState) -> Session:
        now = time.time()
        current = None
        if state.current_session_id:
            current = next(
                (s for s in state.sessions if s.session_id == state.current_session_id), None
            )
        if current is None or now - current.last_activity_at > SESSION_TIMEOUT_SECONDS:
            current = Session(session_id=str(uuid.uuid4()), started_at=now, last_activity_at=now)
            state.sessions.append(current)
            state.current_session_id = current.session_id
            # 会话断了,之前未完成的任务/聚焦对象不该跨会话继承
            state.active_task = None
            state.active_system_flow = None
            state.focused_object = None
            state.pending_turn = None
        return current
