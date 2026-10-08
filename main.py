import uvicorn


def main():
    uvicorn.run("atguigu.api.app:app")


if __name__ == "__main__":
    main()
