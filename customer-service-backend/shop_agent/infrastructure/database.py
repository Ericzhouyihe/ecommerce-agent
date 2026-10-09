from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from shop_agent.conf.config import settings

engine: AsyncEngine | None = None
session_factory: async_sessionmaker[AsyncSession] | None = None


# 创建数据库引擎
def create_db_engine():
    global engine, session_factory
    engine = create_async_engine(url=settings.database_url, echo=False, pool_pre_ping=True)
    session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


# 关闭数据库引擎
async def close_db_engine():
    if engine is not None:
        await engine.dispose()


if __name__ == "__main__":

    async def test():
        await create_db_engine()
        async with session_factory() as session:
            result = await session.execute(text("SELECT 1"))
            data = result.fetchall()
            print(data)
            print(type(data))
            print(type(data[0]))
        await close_db_engine()

    import asyncio

    asyncio.run(test())
"""
# 1. 创建异步数据库引擎
engine = create_async_engine(
    url=settings.database_url,
    echo=False,
    pool_pre_ping=True,
)


# 2. 创建 Session 工厂
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# 3. FastAPI 数据库依赖
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# 4. 应用关闭时释放数据库连接池
async def close_db() -> None:
    await engine.dispose()

"""
