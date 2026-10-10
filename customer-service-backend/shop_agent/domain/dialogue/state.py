from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class DialogueState:
    """与某位用户的完整对话上下文,以 sender_id 为键持久化"""

    sender_id: str
    # 1. 用户任务上下文
    active_task: dict | None = None  # {flow_id, step_id, slots}
    paused_tasks: list[dict] = field(default_factory=list)
    # 2. 系统任务上下文(含 __type__ 标记的子类字典)
    active_system_flow: dict | None = None
    # 3. 聚焦对象
    focused_object: dict | None = None  # {type, id, title, attributes}
    # 4. 会话历史
    sessions: list[dict] = field(default_factory=list)
    current_session_id: str | None = None
    # 5. 处理中的轮次(瞬态,不落盘)
    pending_turn: dict | None = None

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
