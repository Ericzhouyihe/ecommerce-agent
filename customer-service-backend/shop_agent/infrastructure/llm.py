from langchain.chat_models import BaseChatModel, init_chat_model

from shop_agent.conf.config import settings

# llm = ChatOpenAI(
#     api_key=settings.llm_api_key,
#     base_url=settings.llm_base_url,
#     temperature=0,
# )

llm: BaseChatModel = init_chat_model(
    model=settings.llm_model,
    model_provider="openai",
    api_key=settings.llm_api_key,
    base_url=settings.llm_base_url,
    temperature=0,
)

if __name__ == "__main__":
    print(llm.invoke("你好").content)
