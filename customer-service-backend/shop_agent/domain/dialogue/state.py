import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from shop_agent.domain.dialogue.messages import MessageObject, UserMessage
from shop_agent.domain.dialogue.sessions import Session, Turn
from shop_agent.domain.task.contexts import SystemContext, TaskContext


@dataclass
class DialogueState:
    sender_id: str
    active_task: TaskContext | None = None
    paused_tasks: list[TaskContext] = field(default_factory=list)
    active_system_task: SystemContext | None = None
    focused_object: MessageObject | None = None
    sessions: list[Session] = field(default_factory=list)
    current_session_id: str | None = None
    pending_turn: Turn | None = None

    def to_dict(self) -> dict:
        """序列化为可 JSON 持久化的 dict;剔除瞬态字段"""
        return {
            "sender_id": self.sender_id,
            "active_task": self.active_task.to_dict() if self.active_task else None,
            "paused_tasks": [task.to_dict() for task in self.paused_tasks],
            "active_system_task": self.active_system_task.to_dict()
            if self.active_system_task
            else None,
            "focused_object": self.focused_object.to_dict()
            if self.focused_object
            else None,
            "sessions": [session.to_dict() for session in self.sessions],
            "current_session_id": self.current_session_id,
            # "pending_turn": 不持久化,因为是瞬态字段
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DialogueState":
        """从持久化 JSON 重建;忽略未知键,兼容结构演进"""
        active_task_data = data.get("active_task")
        active_system_task_data = data.get("active_system_task")
        return cls(
            sender_id=data["sender_id"],
            active_task=TaskContext.from_dict(active_task_data)
            if active_task_data
            else None,
            paused_tasks=[
                TaskContext.from_dict(task) for task in data.get("paused_tasks", [])
            ],
            active_system_task=SystemContext.from_dict(active_system_task_data)
            if active_system_task_data
            else None,
            focused_object=MessageObject.from_dict(data.get("focused_object"))
            if data.get("focused_object")
            else None,
            sessions=[
                Session.from_dict(session) for session in data.get("sessions", [])
            ],
            current_session_id=data.get("current_session_id"),
        )

    def start_system_task(self, system_context: SystemContext):
        """
        启动系统任务
        :param system_context: 系统任务上下文
        """
        self.active_system_task = system_context

    def end_system_task(self):
        """
        关闭当前的系统任务
        """
        self.active_system_task = None

    def interrupt_active_task(self):
        """
        中断当前任务
        """
        self.paused_tasks.append(self.active_task)
        self.active_task = None

    def start_task(self, task_context: TaskContext):
        """
        启动任务
        :param task_context: 任务上下文
        """
        self.active_task = task_context

    def set_slots(self, slots: dict[str, Any]):
        """
        更新slots(写入业务任务;系统任务运行期间也写到业务任务上)
        :param slots: 要更新的slots
        """
        if self.active_task is not None:
            self.active_task.slots.update(slots)

    def cancel_active_task(self):
        """
        取消当前任务
        """
        self.active_task = None
        self.active_system_task = None

    def resume_task(self, flow_id: str):
        """
        恢复任务
        :param flow_id: 任务所属flow的id
        """
        for task in self.paused_tasks:
            if task.flow_id == flow_id:
                self.active_task = task
                self.paused_tasks.remove(task)
                break

    def current_session(self) -> Session | None:
        """
        获取当前会话
        """
        for session in self.sessions:
            if session.session_id == self.current_session_id:
                return session
        return None

    def current_task(self) -> TaskContext | None:
        """
        获取当前任务(系统任务优先执行)
        """
        return self.active_system_task or self.active_task

    def end_active_task(self):
        """
        关闭当前任务
        """
        self.active_task = None

    def remove_slot(self, slot_name: str):
        """
        删除指定槽位(校验失败时打回重填)
        """
        self.active_task.slots.pop(slot_name, None)

    def start_session(self):
        """
        开启新会话
        """
        now = time.time()
        session = Session(
            session_id=str(uuid.uuid4()), started_at=now, last_activity_at=now
        )
        self.sessions.append(session)
        self.current_session_id = session.session_id

    def close_current_session(self):
        """
        关闭当前会话(超时后由引擎调用)
        """
        session = self.current_session()
        if session is not None:
            session.closed_at = time.time()
        self.current_session_id = None

    def reset_runtime_state_for_new_session(self):
        """
        新会话开始前清空运行时状态:未完成任务不该跨会话继承
        """
        self.active_task = None
        self.active_system_task = None
        self.focused_object = None
        self.paused_tasks = []

    def begin_turn(self, message: UserMessage):
        """
        开启新一轮对话(先挂成 pending,提交时才写入会话)
        """
        self.pending_turn = Turn(
            turn_id=str(uuid.uuid4()), user_message=message, bot_messages=[]
        )

    def commit_pending_turn(self):
        """
        提交本轮对话:写进当前会话,清空 pending
        """
        if self.pending_turn is not None:
            self.current_session().turns.append(self.pending_turn)
        self.pending_turn = None
