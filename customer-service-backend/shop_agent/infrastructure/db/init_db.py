"""一键建表入口:只创建缺失的表,不会更新已有表结构。

用法: uv run python -m shop_agent.infrastructure.db.init_db
"""

import asyncio

from shop_agent.infrastructure.db.database import engine
from shop_agent.infrastructure.db.models import Base


async def init_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("tables created:", list(Base.metadata.tables))


if __name__ == "__main__":
    asyncio.run(init_tables())
