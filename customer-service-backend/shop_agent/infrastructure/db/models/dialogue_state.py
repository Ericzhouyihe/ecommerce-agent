from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from shop_agent.infrastructure.db.models.base import Base


class DialogueStateORM(Base):
    __tablename__ = "dialogue_states"

    sender_id: Mapped[str] = mapped_column(String(255), primary_key=True, comment="用户唯一标识")
    state_json: Mapped[str] = mapped_column(Text, nullable=False, comment="完整对话状态 JSON")


if __name__ == "__main__":
    import asyncio

    from shop_agent.infrastructure.db.database import engine

    async def init_tables() -> None:
        """一键建表(只创建缺失的表,不会更新已有表结构)"""
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("tables created:", list(Base.metadata.tables))

    asyncio.run(init_tables())
