"""异步 HTTP 工具（阶段 0）。"""

from __future__ import annotations

import asyncio
from typing import Any

import httpx


async def fetch_json(
    url: str,
    *,
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
                last_exc = exc
                if attempt < retries:
                    await asyncio.sleep(0.3 * (attempt + 1))
        assert last_exc is not None
        raise last_exc


async def fetch_many(urls: list[str], *, timeout: float = 10.0) -> list[Any | Exception]:
    """并发请求多个 URL；单个失败不拖垮全部。"""

    async def _one(url: str) -> Any | Exception:
        try:
            return await fetch_json(url, timeout=timeout)
        except Exception as exc:  # noqa: BLE001 - 演示聚合错误
            return exc

    return list(await asyncio.gather(*[_one(u) for u in urls]))
