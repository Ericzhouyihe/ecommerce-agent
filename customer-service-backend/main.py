import uvicorn

from shop_agent.conf.config import settings


def main():
    uvicorn.run("shop_agent.app:app", host=settings.app_host, port=settings.app_port)


if __name__ == "__main__":
    main()
