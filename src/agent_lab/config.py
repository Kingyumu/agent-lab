"""全局配置：从环境变量 / .env 加载。

【Python 语法速览】（边学 Agent 边学 Python）
- `from __future__ import annotations`：注解延后求值，可用 `list[str]` 等新写法
- `@property`：把方法当属性读，如 `settings.has_api_key`（不加括号）
- 类型注解 `-> bool`：标明返回值类型，运行时不强制
"""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # [Python] 类变量赋值：给 pydantic 用的「模型配置」，不是实例字段
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # [Python] `字段: 类型 = 默认值`：声明配置项；实际值可被环境变量覆盖
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"

    agent_lab_host: str = "127.0.0.1"
    agent_lab_port: int = 8000
    log_level: str = "INFO"

    @property
    def has_api_key(self) -> bool:
        # [Python] `and` 短路：左边为假则不再算右边；`startswith` 判断前缀
        return bool(self.openai_api_key) and not self.openai_api_key.startswith("sk-your")


# [Python] 模块级单例：import 时创建一次，全项目共用同一配置对象
settings = Settings()
