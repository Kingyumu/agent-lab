"""阶段 9：评测演示。

【Python 语法速览】（边学 Agent 边学 Python）
- `from 包.模块 import 函数`：跨包复用已有入口，避免复制粘贴
- 本文件几乎只有「转发」：`main` 来自 `evals.run_eval`
- `if __name__ == "__main__"`：脚本入口守卫
"""

from __future__ import annotations

# [Python] 直接导入别的模块里的 `main`，本文件当薄封装入口
from evals.run_eval import main


if __name__ == "__main__":
    main()
