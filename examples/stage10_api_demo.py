"""阶段 10：启动 API。

【Python 语法速览】（边学 Agent 边学 Python）
- 字符串形式的导入路径 `"包.模块:对象"`：给 ASGI 服务器按名加载应用
- 关键字参数跨多行：可读性更好，末尾逗号合法
- 从 `settings` 读 host/port：配置与启动代码分离
"""

from __future__ import annotations

import uvicorn

from agent_lab.config import settings


def main() -> None:
    # [Python] 第一个参数是「可导入路径字符串」，不是直接传 app 对象
    uvicorn.run(
        "agent_lab.api.app:app",
        host=settings.agent_lab_host,
        port=settings.agent_lab_port,
        reload=False,
    )


if __name__ == "__main__":
    main()
