import json

from sqlalchemy import select
from sqlalchemy.dialects.mysql import insert as mysql_insert
from sqlalchemy.ext.asyncio import AsyncSession

from shop_agent.domain.dialogue.contexts import TaskContext
from shop_agent.domain.dialogue.repository import DialogueStateRepository
from shop_agent.domain.dialogue.state import DialogueState
from shop_agent.infrastructure.db.models import DialogueStateORM


class MySQLDialogueStateRepository(DialogueStateRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def load_state(self, sender_id: str) -> DialogueState:
        stmt = select(DialogueStateORM).where(DialogueStateORM.sender_id == sender_id)
        result = await self.session.execute(stmt)
        orm = result.scalar_one_or_none()
        if orm is None:
            return DialogueState(sender_id=sender_id)
        return DialogueState.from_dict(json.loads(orm.state_json))

    async def save_state(self, state: DialogueState) -> None:
        stmt = mysql_insert(DialogueStateORM).values(
            sender_id=state.sender_id,
            state_json=json.dumps(state.to_dict(), ensure_ascii=False),
        )
        stmt = stmt.on_duplicate_key_update(state_json=stmt.inserted.state_json)
        await self.session.execute(stmt)
        await self.session.commit()


if __name__ == "__main__":

    async def test():
        from shop_agent.infrastructure.db.database import close_db, session_factory

        try:
            async with session_factory() as session:
                repo = MySQLDialogueStateRepository(session)
                state = DialogueState(
                    sender_id="test_sender",
                    active_task=TaskContext(
                        flow_id="flow_1",
                        step_id="step_1",
                        slots={"order_id": "order_1"},
                    ),
                )
                await repo.save_state(state)
                state = await repo.load_state("test_sender")
                print(state)
        finally:
            await close_db()

    import asyncio

    asyncio.run(test())
