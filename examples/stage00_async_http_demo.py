"""阶段 0：异步并发 HTTP 演示。

【Python 语法速览】（边学 Agent 边学 Python）
- `async def` / `await`：协程；`await` 会把控制权交回事件循环
- `asyncio.run(...)`：从同步入口启动一次异步主函数
- `zip(..., strict=True)`：按位置配对；长度不一致会立刻报错
"""

from __future__ import annotations

import asyncio

from agent_lab.http_utils import fetch_many


async def main() -> None:
    urls = [
        "https://httpbin.org/json",
        "https://httpbin.org/uuid",
        "https://httpbin.org/delay/1",
    ]
    print("并发请求中…")
    # [Python] `await`：等待协程完成并拿到返回值
    results = await fetch_many(urls, timeout=8.0)
    # [Python] `zip(..., strict=True)`：两条序列一一对应，长度必须相同
    for url, result in zip(urls, results, strict=True):
        # [Python] `isinstance`：运行时判断类型；异常对象也可当普通值传递
        if isinstance(result, Exception):
            print(f"[FAIL] {url}: {type(result).__name__}: {result}")
        else:
            # [Python] 条件表达式 `A if 条件 else B`：写成一行的二选一
            keys = list(result)[:5] if isinstance(result, dict) else type(result)
            print(f"[OK]   {url}: {keys}")


if __name__ == "__main__":
    asyncio.run(main())
