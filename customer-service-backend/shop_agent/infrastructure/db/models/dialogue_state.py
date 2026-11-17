from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from shop_agent.infrastructure.db.models.base import Base


class DialogueStateORM(Base):
    __tablename__ = "dialogue_states"

    sender_id: Mapped[str] = mapped_column(String(255), primary_key=True, comment="用户唯一标识")
    state_json: Mapped[str] = mapped_column(
        Text, nullable=False, default="{}", comment="完整对话状态 JSON"
    )
