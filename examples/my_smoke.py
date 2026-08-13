"""最小冒烟：确认包可导入、配置可读取。

【Python 语法速览】（边学 Agent 边学 Python）
- `from 包 import 名`：从已安装/可导入的包里取出符号
- `if __name__ == '__main__'`：仅直接运行本文件时才执行，被 import 时不跑
- 逗号分隔的多个参数：`print(a, b)` 会用空格拼成一行输出
"""

from agent_lab import __version__
from agent_lab.config import settings


# [Python] `__name__` 是模块名；直接运行时为 `'__main__'`
if __name__ == '__main__':
    print(__version__, settings.openai_api_key)
