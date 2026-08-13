"""API 包入口：再导出 FastAPI 应用实例。

【Python 语法速览】（边学 Agent 边学 Python）
- `from ... import ...`：从子模块拉符号到包命名空间，方便 `from agent_lab.api import app`
- `__all__`：列出「from package import *」时公开的名字，也是文档式公开 API 清单
"""

from agent_lab.api.app import app

__all__ = ["app"]
