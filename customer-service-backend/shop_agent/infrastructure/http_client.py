import asyncio

from httpx import AsyncClient

http_client: AsyncClient | None = None


def init_http_client():
    global http_client
    if http_client is not None:
        return
    http_client = AsyncClient()


async def close_http_client():
    global http_client
    if http_client is not None:
        await http_client.aclose()
        http_client = None


if __name__ == "__main__":

    async def test():
        init_http_client()

        response = await http_client.get("http://localhost:18081/users/u1001/orders")
        print(response.json())

        await close_http_client()

    asyncio.run(test())
