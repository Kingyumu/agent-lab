"""阶段 0：异步并发 HTTP 演示。"""

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
    results = await fetch_many(urls, timeout=8.0)
    for url, result in zip(urls, results, strict=True):
        if isinstance(result, Exception):
            print(f"[FAIL] {url}: {type(result).__name__}: {result}")
        else:
            keys = list(result)[:5] if isinstance(result, dict) else type(result)
            print(f"[OK]   {url}: {keys}")


if __name__ == "__main__":
    asyncio.run(main())
