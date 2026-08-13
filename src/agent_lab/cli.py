"""简单 CLI 入口。

【Python 语法速览】（边学 Agent 边学 Python）
- `if __name__ == "__main__"`：仅直接运行本文件时为真；被 import 时不执行
- `-> None`：标注函数无有意义返回值
"""

from __future__ import annotations


def main() -> None:
    print("agent-lab 已安装。请从 README.md 开始学习。")
    print("示例：python examples/stage03_tool_agent_demo.py --mock")


# [Python] 脚本入口守卫：`python -m agent_lab.cli` 或直接运行时才会调 main()
if __name__ == "__main__":
    main()
