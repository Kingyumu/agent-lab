"""异步 HTTP 工具（阶段 0）。

【Python 语法速览】（边学 Agent 边学 Python）
- `async def` / `await`：协程；遇到 I/O 可让出执行权
- `*` 后的参数：必须关键字传入，如 `timeout=10.0`
- `async with`：异步上下文管理器，退出时自动关闭资源
- `asyncio.gather`：并发跑多个协程
"""

from __future__ import annotations

import asyncio
from typing import Any

import httpx


async def fetch_json(
    url: str,
    *,
    # [Python] * 后面的参数必须用关键字传入，如 timeout=10.0
    timeout: float = 10.0,
    retries: int = 2,
    headers: dict[str, str] | None = None,
) -> Any:
    """GET JSON，带超时与有限重试。"""
    last_exc: Exception | None = None
    async with httpx.AsyncClient(timeout=timeout, headers=headers) as client:
        for attempt in range(retries + 1):
            try:
                resp = await client.get(url)
                resp.raise_for_status()
                return resp.json()
            except (httpx.HTTPError, ValueError) as exc:
                # [Python] `as exc`：把捕获的异常绑定到变量，便于重试后重新抛出
                last_exc = exc
                if attempt < retries:
                    await asyncio.sleep(0.3 * (attempt + 1))
        # [Python] `assert`：开发期断言；此处保证下面 raise 时 last_exc 非空
        assert last_exc is not None
        raise last_exc


async def fetch_many(urls: list[str], *, timeout: float = 10.0) -> list[Any | Exception]:
    """并发请求多个 URL；单个失败不拖垮全部。"""

    async def _one(url: str) -> Any | Exception:
        # [Python] 嵌套函数：可闭包外层的 `timeout`
        try:
            return await fetch_json(url, timeout=timeout)
        except Exception as exc:  # noqa: BLE001 - 演示聚合错误
            return exc

    # [Python] `*[...]`：把列表拆成 gather 的多个位置参数
    return list(await asyncio.gather(*[_one(u) for u in urls]))
