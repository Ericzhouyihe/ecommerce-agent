from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

# 统一的约束命名规则:Alembic autogenerate 生成迁移时,
# 索引/外键/唯一约束的名字才稳定可复现,不会出现 MySQL 随机命名
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """所有 ORM 模型的声明基类"""

    metadata = MetaData(naming_convention=NAMING_CONVENTION)
