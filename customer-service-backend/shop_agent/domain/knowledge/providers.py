import asyncio
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from shop_agent.conf.config import settings
from shop_agent.domain.dialogue.messages import MessageObject
from shop_agent.domain.dialogue.state import DialogueState
from shop_agent.infrastructure import http_client


@dataclass
class KnowledgeChunk:
    content: str


class KnowledgeProvider(ABC):
    provider_id = ""

    @abstractmethod
    async def retrieve(
        self,
        state: DialogueState,
    ) -> list[KnowledgeChunk]:
        pass


class ProductAPIProvider(KnowledgeProvider):
    provider_id = "api.product"

    async def retrieve(self, state: DialogueState) -> list[KnowledgeChunk]:
        if state.focused_object is None:
            return [KnowledgeChunk(content="未提供商品信息")]
        product_id = state.focused_object.id
        data = await self._get_product_info_by_id(product_id)
        if data is None:
            return [KnowledgeChunk(content="暂时无法查到该商品信息")]
        text = json.dumps(data, ensure_ascii=False, indent=2)
        return [KnowledgeChunk(content=f"商品信息:\n{text}")]

    async def _get_product_info_by_id(self, product_id: str) -> dict[str, Any] | None:
        try:
            url = f"{settings.commerce_api_base_url}/products/{product_id}"
            response = await http_client.get_http_client().get(url)
            return response.json()["data"]
        except asyncio.CancelledError:
            return None


class OrderAPIProvider(KnowledgeProvider):
    provider_id = "api.order"

    async def retrieve(self, state: DialogueState) -> list[KnowledgeChunk]:
        if state.focused_object is None:
            return [KnowledgeChunk(content="未提供订单信息")]
        order_number = state.focused_object.id

        order_payload, logistics_payload = await asyncio.gather(
            self._fetch_order(order_number),
            self._fetch_logistics(order_number),
        )

        return [
            KnowledgeChunk(
                content="订单与物流信息：\n"
                + json.dumps(
                    {
                        "order_number": order_number,
                        "order": order_payload,
                        "logistics": logistics_payload,
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
        ]

    async def _fetch_order(self, order_number) -> dict[str, Any] | None:
        try:
            url = f"{settings.commerce_api_base_url}/orders/{order_number}"
            response = await http_client.get_http_client().get(url)
            return response.json()["data"]
        except Exception:
            return None

    async def _fetch_logistics(self, order_number) -> dict[str, Any] | None:
        try:
            url = f"{settings.commerce_api_base_url}/orders/{order_number}/logistics"
            response = await http_client.get_http_client().get(url)
            return response.json().get("data", {})
        except Exception:
            return None


class FAQProvider(KnowledgeProvider):
    provider_id = "faq.default"

    async def retrieve(self, state: DialogueState) -> list[KnowledgeChunk]:
        return [KnowledgeChunk(content="未检索到相关问题")]


class RAGProvider(KnowledgeProvider):
    provider_id = "rag.default"

    async def retrieve(self, state: DialogueState) -> list[KnowledgeChunk]:
        return [KnowledgeChunk(content="未检索到相关信息")]


if __name__ == "__main__":
    provider = OrderAPIProvider()
    state = DialogueState(
        sender_id="u1", focused_object=MessageObject(id="A20260410001", type="order")
    )
    http_client.init_http_client()

    async def test():
        chunks = await provider.retrieve(state)
        print(chunks[0].content)

        await http_client.close_http_client()

    asyncio.run(test())