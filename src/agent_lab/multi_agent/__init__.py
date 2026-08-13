"""多 Agent 包入口：再导出流水线相关符号。

【Python 语法速览】（边学 Agent 边学 Python）
- 从子模块 import 再挂到包上：`from agent_lab.multi_agent import ResearchWriterPipeline`
- `__all__`：公开导出清单，标明包的稳定接口
"""

from agent_lab.multi_agent.pipeline import MultiAgentResult, ResearchWriterPipeline

__all__ = ["MultiAgentResult", "ResearchWriterPipeline"]
