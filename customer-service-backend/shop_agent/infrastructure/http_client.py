import asyncio

from httpx import AsyncClient

http_client: AsyncClient | None = None


def init_http_client() -> None:
    global http_client
    if http_client is None:
        http_client = AsyncClient()


def get_http_client() -> AsyncClient:
    if http_client is None:
        raise RuntimeError("HTTP client has not been initialized")

    return http_client


async def close_http_client() -> None:
    global http_client
    if http_client is not None:
        await http_client.aclose()
        http_client = None


if __name__ == "__main__":

    async def test() -> None:
        init_http_client()
        try:
            client = get_http_client()
            response = await client.get("http://localhost:18081/users/u1001/orders")
            print(response.json())
        finally:
            await close_http_client()

    asyncio.run(test())
