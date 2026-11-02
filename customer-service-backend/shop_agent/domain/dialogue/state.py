from dataclasses import dataclass, field

from shop_agent.domain.dialogue.messages import MessageObject
from shop_agent.domain.dialogue.sessions import Session, Turn
from shop_agent.domain.task.contexts import (
    SystemContext,
    TaskContext,
    system_context_from_dict,
)


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
            "focused_object": self.focused_object.to_dict() if self.focused_object else None,
            "sessions": [session.to_dict() for session in self.sessions],
            "current_session_id": self.current_session_id,
            # "pending_turn": 不持久化,因为是瞬态字段
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DialogueState":
        """从持久化 JSON 重建;忽略未知键,兼容结构演进"""
        return cls(
            sender_id=data["sender_id"],
            active_task=TaskContext.from_dict(data["active_task"]) if data["active_task"] else None,
            paused_tasks=[TaskContext.from_dict(task) for task in data.get("paused_tasks", [])],
            active_system_task=system_context_from_dict(data["active_system_task"])
            if data.get("active_system_task")
            else None,
            focused_object=MessageObject.from_dict(data.get("focused_object"))
            if data.get("focused_object")
            else None,
            sessions=[Session.from_dict(session) for session in data.get("sessions", [])],
            current_session_id=data.get("current_session_id"),
        )

    def start_system_task(self, system_context: SystemContext):
        """
        启动系统任务
        :param system_context:
        :return:
        """
        self.active_system_task = system_context

    def end_system_task(self):
        """
        关闭当前的系统任务
        :return:
        """
        self.active_system_task = None

    def interrupt_active_task(self):
        """
        中断当前任务
        :return:
        """
        self.paused_tasks.append(self.active_task)
        self.active_task = None

    def start_task(self, task_context: TaskContext):
        """
        启动任务
        :param task_context:
        :return:
        """
        self.active_task = task_context
