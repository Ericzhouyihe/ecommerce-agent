import time
import uuid

from shop_agent.domain.dialogue.handlers.chitchat_handler import handle_chitchat
from shop_agent.domain.dialogue.handlers.task_handler import handle_task
from shop_agent.domain.dialogue.messages import BotMessage, MessageType, ProcessResult, UserMessage
from shop_agent.domain.dialogue.planner.turn_plan_validator import validate_turn_plan
from shop_agent.domain.dialogue.planner.turn_planner import TurnKind, plan_turn
from shop_agent.domain.dialogue.sessions import Session, Turn
from shop_agent.domain.dialogue.state import DialogueState

SESSION_TIMEOUT_SECONDS = 60 * 30


class DialogueEngine:
    async def process_message(
        self, dialogue_state: DialogueState, user_message: UserMessage
    ) -> ProcessResult:
        # 1.准备会话
        session = self._prepare_session(dialogue_state)

        # 2.创建本轮 Turn(先挂成 pending,提交时才转正)
        turn = Turn(
            turn_id=str(uuid.uuid4()),
            input_message=user_message,
            assistant_messages=[],
        )
        dialogue_state.pending_turn = turn

        # 3.处理本轮消息
        if user_message.type == MessageType.OBJECT:
            # TODO: 对象消息旁路：暂不分类，后续接槽位匹配
            dialogue_state.focused_object = user_message.object
            # replies = [BotMessage(text="收到对象消息(待实现)")]
        else:
            # 文本消息: 分类 -> 校验 -> 回复
            plan = await plan_turn(user_message.text or "", session)
            plan = await validate_turn_plan(plan, dialogue_state)

            match plan.kind:
                case TurnKind.TASK:
                    replies = [await handle_task(plan, dialogue_state)]
                case TurnKind.CHITCHAT:
                    # TODO: 闲聊回复待实现
                    replies = [await handle_chitchat(user_message.text or "", session)]
                case TurnKind.KNOWLEDGE:
                    # TODO: 知识问答待实现
                    replies = [BotMessage(text="知识问答(待实现)")]  # 第4步再接
                case _:
                    # TODO: 无效分类待实现
                    replies = [BotMessage(text="抱歉，我没太理解你的意思，能说得更具体些吗？")]

        turn.assistant_messages.extend(replies)

        # 4.提交本轮:写进 session,清空 pending_turn
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
