from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# 允许用项目根目录的 .env 提供默认配置(不覆盖已存在的环境变量)
load_dotenv(Path(__file__).parents[1] / ".env", override=False)


@dataclass(frozen=True)
class Settings:
    database_url: str = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://zhouyihe:zhouyihe.123@127.0.0.1:3306/commerce?charset=utf8mb4",
    )
    app_host: str = os.getenv("APP_HOST", "0.0.0.0")
    app_port: int = int(os.getenv("APP_PORT", "18081"))


settings = Settings()
