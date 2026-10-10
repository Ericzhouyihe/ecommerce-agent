from dataclasses import dataclass


@dataclass
class OrderRef:
    """值对象：用户引用的订单"""

    order_id: str
    source: str


@dataclass
class Message:
    """领域实体：客服会话中的一条消息"""

    sender_id: str
    text: str
    attached_order: OrderRef | None

    @property
    def needs_order_lookup(self) -> bool:  # ← 行为跟着数据走，这是实体的标志
        return self.attached_order is not None
