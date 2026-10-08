import asyncio

import httpx

http_client = httpx.AsyncClient()

if __name__ == "__main__":

    async def test():
        response = await http_client.get("http://localhost:18081/users/u1001/orders")
        print(response.json())

        await http_client.aclose()

    asyncio.run(test())
