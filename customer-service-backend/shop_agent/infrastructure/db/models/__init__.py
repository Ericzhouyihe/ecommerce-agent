# 统一 import 所有 ORM 模型:
# Alembic autogenerate / Base.metadata.create_all 都依赖这里的注册,
# 漏 import 会导致新表静默不创建
from .base import Base
from .dialogue_state import DialogueStateORM

__all__ = ["Base", "DialogueStateORM"]
