from dataclasses import dataclass, field

from shop_agent.domain.dialogue.contexts import SystemContext, TaskContext
from shop_agent.domain.dialogue.messages import MessageObject
from shop_agent.domain.dialogue.sessions import Session, Turn


@dataclass
class DialogueState:
    sender_id: str
    active_task: TaskContext | None = None
    paused_tasks: list[TaskContext] = field(default_factory=list)
    active_system_flow: SystemContext | None = None
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
            "active_system_flow": self.active_system_flow.to_dict()
            if self.active_system_flow
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
            active_system_flow=SystemContext.from_dict(data.get("active_system_flow"))
            if data.get("active_system_flow")
            else None,
            focused_object=MessageObject.from_dict(data.get("focused_object"))
            if data.get("focused_object")
            else None,
            sessions=[Session.from_dict(session) for session in data.get("sessions", [])],
            current_session_id=data.get("current_session_id"),
        )
