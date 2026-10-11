import json

from sqlalchemy import delete, func, select
from sqlalchemy.dialects.mysql import insert as mysql_insert
from sqlalchemy.ext.asyncio import AsyncSession

from shop_agent.domain.dialogue.state import DialogueState
from shop_agent.infrastructure.db.models import DialogueStateORM


class DialogueStateRepository:
    """以 sender_id 为键,对对话状态做增删查改"""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ========================= 查 =========================
    async def get(self, sender_id: str) -> DialogueState | None:
        """按主键查一行;不存在返回 None"""
        row = await self.db.get(DialogueStateORM, sender_id)
        if row is None:
            return None
        return DialogueState.from_dict(json.loads(row.state_json))

    async def load(self, sender_id: str) -> DialogueState:
        """查;不存在则返回全新状态(service 常用,省一次判空)"""
        state = await self.get(sender_id)
        return state if state is not None else DialogueState(sender_id=sender_id)

    async def exists(self, sender_id: str) -> bool:
        stmt = (
            select(func.count())
            .select_from(DialogueStateORM)
            .where(DialogueStateORM.sender_id == sender_id)
        )
        return bool(await self.db.scalar(stmt))

    # ========================= 增 / 改 =========================
    async def save(self, state: DialogueState) -> None:
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

    # ========================= 删 =========================
    async def delete(self, sender_id: str) -> bool:
        """删除该用户的全部对话状态;返回是否真的删了"""
        stmt = delete(DialogueStateORM).where(DialogueStateORM.sender_id == sender_id)
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0


if __name__ == "__main__":

    async def test() -> None:
        from shop_agent.infrastructure.db.database import close_db, session_factory

        async with session_factory() as db:
            repo = DialogueStateRepository(db)

            # 增:带一个 pending_turn,验证它不会被持久化
            state = DialogueState(
                sender_id="user_test_001",
                active_task={
                    "flow_id": "refund_request",
                    "step_id": "ask_refund_reason",
                    "slots": {"order_number": "10001"},
                },
            )
            state.pending_turn = {"turn_id": "t1"}
            await repo.save(state)
            print("saved:", await repo.get("user_test_001"))

            # 改:整行覆盖
            loaded = await repo.load("user_test_001")
            loaded.active_task = None
            await repo.save(loaded)
            print("updated:", await repo.load("user_test_001"))

            # 删
            print("deleted:", await repo.delete("user_test_001"))
            print("after delete:", await repo.get("user_test_001"))

        await close_db()

    import asyncio

    asyncio.run(test())
