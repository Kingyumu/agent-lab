"""LLM 客户端实现（便于 `from agent_lab.llm.client import ...`）。"""

from agent_lab.llm import (  # noqa: F401
    ChatMessage,
    ChatResult,
    MockLLMClient,
    OpenAICompatClient,
    build_default_client,
)
