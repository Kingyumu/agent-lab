"""LLM 客户端实现（便于 `from agent_lab.llm.client import ...`）。

【Python 语法速览】（边学 Agent 边学 Python）
- 再导出：本模块从包内 `__init__` 导入并暴露同名符号，方便旧路径 import
- `# noqa: F401`：告诉 linter「未直接使用的 import」是故意的（供外部再导出）
"""

from agent_lab.llm import (  # noqa: F401
    ChatMessage,
    ChatResult,
    MockLLMClient,
    OpenAICompatClient,
    build_default_client,
)
