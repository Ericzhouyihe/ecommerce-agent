from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = Path(__file__).parents[2] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # =========================
    # 应用
    # =========================
    app_name: str = "Shop Agent"
    app_version: str = "1.0.0"
    app_host: str = "127.0.0.1"
    app_port: int = 18082

    # =========================
    # LLM
    # =========================
    llm_base_url: str = "https://open.bigmodel.cn/api/coding/paas/v4"
    llm_api_key: str = ""
    llm_model: str = "GLM-5.3"
    openai_base_url: str = ""
    openai_api_key: str = ""
    openai_model: str = ""

    # =========================
    # MySQL
    # =========================
    database_url: str = (
        "mysql+aiomysql://zhouyihe:zhouyihe.123@127.0.0.1:3306/customer_service?charset=utf8mb4"
    )

    # =========================
    # 商城 API
    # =========================
    commerce_api_base_url: str = "http://127.0.0.1:18081"

    # =========================
    # Redis
    # =========================
    redis_url: str = "redis://localhost:6379"
    redis_password: str = ""

    # =========================
    # Milvus
    # =========================
    milvus_uri: str = "http://127.0.0.1:19530"
    milvus_token: str = ""

    # =========================
    # Embedding
    # bge-m3 输出 1024 维，bge-small-zh-v1.5 输出 512 维
    # =========================
    embedding_name: str = "bge-small-zh-v1.5"
    embedding_dim: int = 512


settings = Settings()

if __name__ == "__main__":
    print(settings.llm_api_key)
