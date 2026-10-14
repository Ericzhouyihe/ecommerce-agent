from __future__ import annotations

from dataclasses import dataclass, field

from shop_agent.domain.dialogue.contexts import SystemContext, TaskContext
from shop_agent.domain.dialogue.messages import MessageObject
from shop_agent.domain.dialogue.sessions import Turn


@dataclass
class DialogueState:
    sender_id: str
    active_task: TaskContext | None = None
    paused_tasks: list[TaskContext] = field(default_factory=list)
    active_system_flow: SystemContext | None = None
    focused_object: MessageObject | None = None
    sessions: list[dict] = field(default_factory=list)
    current_session_id: str | None = None
    pending_turn: Turn | None = None

    def to_dict(self) -> dict:
        """序列化为可 JSON 持久化的 dict;剔除瞬态字段"""
        return {
            "sender_id": self.sender_id,
            "active_task": self.active_task,
            "paused_tasks": self.paused_tasks,
            "active_system_flow": self.active_system_flow,
            "focused_object": self.focused_object,
            "sessions": self.sessions,
            "current_session_id": self.current_session_id,
            # pending_turn 故意不导出:两步提交,未完成的轮次不落盘
        }

    @classmethod
    def from_dict(cls, data: dict) -> DialogueState:
        """从持久化 JSON 重建;忽略未知键,兼容结构演进"""
        return cls(
            sender_id=data["sender_id"],
            active_task=data.get("active_task"),
            paused_tasks=data.get("paused_tasks", []),
            active_system_flow=data.get("active_system_flow"),
            focused_object=data.get("focused_object"),
            sessions=data.get("sessions", []),
            current_session_id=data.get("current_session_id"),
        )
