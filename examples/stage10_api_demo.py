"""阶段 10：启动 API。"""

from __future__ import annotations

import uvicorn

from agent_lab.config import settings


def main() -> None:
    uvicorn.run(
        "agent_lab.api.app:app",
        host=settings.agent_lab_host,
        port=settings.agent_lab_port,
        reload=False,
    )


if __name__ == "__main__":
    main()
