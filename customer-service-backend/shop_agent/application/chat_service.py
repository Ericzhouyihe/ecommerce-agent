from shop_agent.api.v1.scheme import ChatMessage
from shop_agent.domain.message import Message, OrderRef


class ChatService:
    async def handle(self, req: ChatMessage) -> ...:
        # DTO → 领域对象（转换只发生在这一层）
        domain_msg = Message(
            sender_id=req.sender_id,
            text=req.text,
            attached_order=OrderRef(
                order_id=req.object.id,
                source=req.object.attributes.get("source", ""),
            )
            if req.object
            else None,
        )
        if domain_msg.needs_order_lookup:
            order = await self.order_repo.get(domain_msg.attached_order.order_id)
