import json

from sqlalchemy.dialects.mysql import insert as mysql_insert
from sqlalchemy.ext.asyncio import AsyncSession

from shop_agent.domain.dialogue.repository import DialogueStateRepository
from shop_agent.domain.dialogue.state import DialogueState
from shop_agent.infrastructure.db.models import DialogueStateORM


class MySQLDialogueStateRepository(DialogueStateRepository):
    """以 sender_id 为键,对对话状态做增删查改(SQLAlchemy + MySQL 实现)"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def load_state(self, sender_id: str) -> DialogueState:
        """查;不存在则返回全新状态(service 常用,省一次判空)"""
        state = await self.get(sender_id)
        return state if state is not None else DialogueState(sender_id=sender_id)

    async def save_state(self, sender_id: str, state: DialogueState) -> None:
        """upsert:不存在则插入,存在则整行覆盖(快照式写法)

        说明:当前 repo 内部直接 commit。将来若一个请求要写多张表
        (如同时写 turns 表),应把 commit 上移到 service 统一管理事务。
        """
        stmt = mysql_insert(DialogueStateORM).values(
            sender_id=state.sender_id,
            state_json=json.dumps(
                state.to_dict(), ensure_ascii=False
            ),  # to_dict 已剔除 pending_turn
        )
        stmt = stmt.on_duplicate_key_update(state_json=stmt.inserted.state_json)
        await self.db.execute(stmt)
        await self.db.commit()
