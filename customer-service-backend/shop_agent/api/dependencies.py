from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from shop_agent.application.builder import build_dialogue_engine
from shop_agent.application.dialogue_service import DialogueService
from shop_agent.domain.dialogue.engine import DialogueEngine
from shop_agent.domain.dialogue.repository import DialogueStateRepository
from shop_agent.infrastructure.db import database
from shop_agent.infrastructure.repositories.dialogue_state import (
    MySQLDialogueStateRepository,
)

_dialogue_engine: DialogueEngine | None = None


def init_dialogue_engine() -> None:
    """应用启动时装配一次对话引擎(全局单例,无状态可复用)。"""
    global _dialogue_engine
    _dialogue_engine = build_dialogue_engine()


def get_engine() -> DialogueEngine:
    return _dialogue_engine


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with database.session_factory() as session:
        yield session


def get_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> DialogueStateRepository:
    return MySQLDialogueStateRepository(db)


def get_dialogue_service(
    engine: Annotated[DialogueEngine, Depends(get_engine)],
    repository: Annotated[DialogueStateRepository, Depends(get_repository)],
) -> DialogueService:
    return DialogueService(
        dialogue_state_repository=repository, dialogue_engine=engine
    )
