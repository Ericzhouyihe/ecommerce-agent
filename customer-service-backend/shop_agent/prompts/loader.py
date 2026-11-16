from pathlib import Path

PROMPT_DIR = Path(__file__).parent / "jinja2"


def load_prompt(name: str) -> str:
    """按名字加载 jinja2 提示词模板(不含扩展名)。"""
    path = PROMPT_DIR / f"{name}.jinja2"
    return path.read_text(encoding="utf-8")
