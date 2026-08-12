# 第0章第2节：异步与 HTTP

## 写在前面

Agent 工作时，大部分时间不是在「算数学」，而是在**等待**：

- 等大模型回复
- 等搜索接口
- 等数据库
- 等网页下载

如果用普通同步写法，这些等待会一个接一个排队，很慢。  
本节学习用 `asyncio` + `httpx` 做等待中的并发。

---

## 本节你将学会

1. `async` / `await` 在说什么（用人话）
2. 为什么 Agent 几乎总是异步的
3. 运行一个「同时请求多个网址」的示例并看懂

---

## 先用一个生活例子

你在食堂打饭：

**同步（排队）**

```text
买菜 → 等5分钟
买饭 → 再等5分钟
买汤 → 再等5分钟
总共约15分钟
```

**异步并发（饭做好了再取）**

```text
先都取号（发起三个等待）
哪个好了先处理哪个
总等待接近「最慢那一个」，而不是三者相加
```

`await` 的含义很像：  
「这件事要等结果，我先去干别的；好了再回来继续。」

---

## 一步一步讲清楚

### 第1步：普通函数 vs 异步函数

```python
def add(a, b):
    return a + b
```

调用立刻得到结果。

```python
async def fetch_title(url):
    # 里面会 await 网络请求
    ...
```

调用 `fetch_title(url)` **不会立刻得到标题**，只得到一个「协程对象」（可以理解为未完成的任务）。  
必须用 `await fetch_title(url)`，或交给 `asyncio.run` / `asyncio.gather` 去执行。

### 第2步：最小异步程序长这样

```python
import asyncio

async def main():
    print("开始")
    await asyncio.sleep(1)  # 假装等待网络1秒
    print("结束")

asyncio.run(main())
```

记住两个固定搭配：

- 定义：`async def`
- 启动入口：`asyncio.run(main())`
- 等待：`await ...`

### 第3步：并发用 gather

```python
results = await asyncio.gather(
    fetch_json(url1),
    fetch_json(url2),
    fetch_json(url3),
)
```

三个请求一起等，总耗时通常接近最慢的那个。

### 第4步：超时为什么是生命线

工具或模型如果一直不返回，你的 Agent 会永远卡住。  
所以真实项目里，网络调用几乎都要设置 timeout（超时）。

本仓库的 `fetch_json` 就带了 timeout 和有限重试。

### 第5步：和 Agent 的关系（先记住）

后面第3章的 Agent 循环，每一步都可能：

1. await 调用大模型  
2. await 执行工具（工具内部又可能访问网络）  
3. 再 await 调用大模型  

所以第0章先把异步读顺，第3章不会在语法上卡死。

---

## 打开代码一起看（逐行教材版）

下面把两个文件拆开讲。你可以对照源码，一行行往下读。

---

### A. 先看演示脚本：`examples/stage00_async_http_demo.py`

这个文件只做三件事：**准备网址 → 一起请求 → 打印结果**。

#### 第 1–7 行：导入

```python
from __future__ import annotations  # 让类型写法更宽松（可先忽略）
import asyncio                      # Python 自带的异步工具箱
from agent_lab.http_utils import fetch_many  # 我们自己写的「一次请求多个网址」
```

#### 第 10–16 行：准备 3 个测试网址

```python
async def main() -> None:
    urls = [
        "https://httpbin.org/json",    # 返回一段 JSON
        "https://httpbin.org/uuid",    # 返回一个随机 id
        "https://httpbin.org/delay/1", # 故意晚 1 秒再返回（用来体会“等待”）
    ]
```

`httpbin.org` 是专门给人测试 HTTP 用的网站，不是业务系统。

注意：`main` 前面有 `async`，所以它是**异步函数**。  
异步函数不能直接 `main()` 完事，最后要用 `asyncio.run(main())` 启动（见文件末尾）。

#### 第 17–18 行：真正发请求

```python
print("并发请求中…")
results = await fetch_many(urls, timeout=8.0)
```

人话翻译：

> 请同时去请求这三个网址；每个最多等 8 秒；等全部有结果后，把结果列表给我。

- `await` = 这里要等 `fetch_many` 做完  
- 做完后，`results` 是一个列表，长度和 `urls` 一样，一一对应

#### 第 19–23 行：逐个打印成功或失败

```python
for url, result in zip(urls, results, strict=True):
    if isinstance(result, Exception):
        print(f"[FAIL] {url}: ...")   # 这个网址失败了
    else:
        print(f"[OK]   {url}: ...")   # 成功了，简单打印一点内容
```

- `zip(urls, results)`：把「网址」和「结果」配对  
- `strict=True`：两边长度必须一样，否则报错（防止对错位）  
- 为什么结果可能是 `Exception`？因为 `fetch_many` 设计成：**某个网址挂了，其它还继续**，失败对象会放进结果列表，而不是整个程序直接崩掉

#### 第 26–27 行：程序入口

```python
if __name__ == "__main__":
    asyncio.run(main())
```

人话：

> 只有你直接运行这个文件时，才启动异步主函数。  
> `asyncio.run(...)` = 打开异步引擎，跑完再关掉。

---

### B. 再看工具库：`src/agent_lab/http_utils.py`

演示脚本只负责「用」；真正请求逻辑在这里。

这里有两个函数：

1. `fetch_json`：请求 **一个** 网址，拿到 JSON  
2. `fetch_many`：请求 **多个** 网址（内部多次调用 `fetch_json`）

---

#### B1. `fetch_json`：请求一个网址（带超时 + 重试）

函数签名：

```python
async def fetch_json(
    url: str,                 # 要请求的网址
    *,                        # * 后面的参数必须写名字，如 timeout=10
    timeout: float = 10.0,    # 最多等多久（秒）
    retries: int = 2,         # 失败后再试几次（默认还能再试 2 次）
    headers: dict[str, str] | None = None,  # 可选的请求头
) -> Any:                     # 返回解析后的 JSON（常见是 dict）
```

整体流程（请在脑子里放电影）：

```text
创建异步 HTTP 客户端
   ↓
第 1 次尝试请求
   ↓ 成功？ → 返回 JSON，结束
   ↓ 失败？ → 等一会儿，再试
第 2 次尝试……
   ↓
还是失败 → 把最后一次错误抛出去
```

对应代码拆解：

```python
last_exc: Exception | None = None
```

用来记住「最后一次失败原因」。如果全部重试都失败，最后把它抛出。

```python
async with httpx.AsyncClient(timeout=timeout, headers=headers) as client:
```

人话：

> 打开一个异步浏览器客户端；用完自动关闭。  
> `timeout=timeout` 表示这个客户端默认请求超时时间。

`async with` 很像 `with open(...)`：进入时创建，离开时清理。

```python
for attempt in range(retries + 1):
```

如果 `retries=2`，则 `range(3)` → 尝试 0、1、2，共 **3 次**  
（1 次首次 + 2 次重试）。

```python
try:
    resp = await client.get(url)   # 真正发 GET 请求，等待响应
    resp.raise_for_status()        # 若状态码是 4xx/5xx，主动当错误
    return resp.json()             # 把响应正文解析成 Python 对象（dict/list 等）
```

- `await client.get(url)`：这行会「等网络」  
- `raise_for_status()`：比如 404、500 不要当成功  
- `resp.json()`：把 `{"a":1}` 这种文本变成 Python 字典

```python
except (httpx.HTTPError, ValueError) as exc:
    last_exc = exc
    if attempt < retries:
        await asyncio.sleep(0.3 * (attempt + 1))
```

失败时：

1. 记下错误  
2. 如果还有重试机会，就先 `sleep` 一会儿再试  
3. 等待时间：`0.3`、`0.6`… 逐渐变长（避免疯狂连打）

```python
assert last_exc is not None
raise last_exc
```

如果 for 循环结束还没 `return`，说明全失败了，把最后错误抛给调用方。

---

#### B2. `fetch_many`：同时请求多个网址

```python
async def fetch_many(urls: list[str], *, timeout: float = 10.0) -> list[Any | Exception]:
```

返回值类型 `list[Any | Exception]` 的人话：

> 返回一个列表；每一项要么是成功的 JSON，要么是一个异常对象。

内部先定义「请求一个，且自己吞掉异常」的小函数：

```python
async def _one(url: str) -> Any | Exception:
    try:
        return await fetch_json(url, timeout=timeout)  # 成功：返回 JSON
    except Exception as exc:
        return exc                                      # 失败：返回错误对象（不往外炸）
```

为什么要吞掉？  
因为我们希望：**A 网址挂了，不要连累 B、C 也中断。**

最后一行是并发关键：

```python
return list(await asyncio.gather(*[_one(u) for u in urls]))
```

拆开看：

1. `[_one(u) for u in urls]`  
   给每个网址创建一个异步任务（还没跑完，只是任务列表）

2. `*`  
   把列表拆成多个参数，相当于：  
   `gather(任务1, 任务2, 任务3)`

3. `asyncio.gather(...)`  
   **一起等待**这些任务完成（并发，不是一个做完再做下一个）

4. `list(...)`  
   把结果整理成普通列表返回

时间关系对比：

```text
串行：  |--url1--|  |--url2--|  |--url3--|     总时长≈相加
并发：  |--url1---------|
        |--url2------|
        |--url3-----------|                   总时长≈最慢那个
```

---

### C. 两份代码如何配合（一张总图）

```text
stage00_async_http_demo.py
    main()
      └─ await fetch_many([url1, url2, url3])
              │
              ├─ gather 同时启动
              │    _one(url1) → fetch_json(url1)
              │    _one(url2) → fetch_json(url2)
              │    _one(url3) → fetch_json(url3)
              │
              └─ 得到 [结果1, 结果2, 结果3]
                   └─ demo 里 for 循环打印 [OK]/[FAIL]
```

---

### D. 运行演示

```powershell
python examples/stage00_async_http_demo.py
```

你应看到若干 `[OK]`。如果网络不通，可能出现 `[FAIL]`——这本身也是在演示「失败可捕获」。

若全部失败：检查网络/代理；也可以先把上面逐行讲解读完，网络好了再跑。
---

## 动手做

### 练习 A（必做）

在 `examples/stage00_async_http_demo.py` 里，把其中一个 URL 改成明显错误的地址（例如 `https://httpbin.org/status/500`），再运行。  
观察：其它请求是否仍可能成功？这就是「局部失败不影响全局」的意义。

### 练习 B（必做）

阅读并口述（可写在笔记里）：

> `await` 不是「让程序变慢」，而是「这里要等结果；等待期间事件循环可以去做别的任务」。

### 练习 C（选做）

给某个请求加上：

```python
await asyncio.wait_for(fetch_json(url), timeout=0.001)
```

看它是否很快因超时失败。（0.001 秒极短，几乎必超时）

---

## 常见卡点问答

**Q：为什么我在 async 函数里写了 `time.sleep(5)`，整个程序卡死？**  
A：`time.sleep` 会堵住事件循环。异步等待请用 `await asyncio.sleep(5)`。

**Q：所有代码都必须异步吗？**  
A：不是。纯计算、本地小函数可以同步。但「等网络/等模型」的链路，本教材统一走异步，避免两套风格混用。

**Q：报错 `SyntaxError: await outside async function`？**  
A：`await` 只能写在 `async def` 里面。

---

## 本节小结

- Agent 大量时间在等待 I/O，所以用异步
- `async def` + `await` + `asyncio.run` 是最小闭环
- `gather` 用于并发；timeout 用于防止永久卡住

---

## 课后阅读（怎么读）

- [asyncio 任务与协程](https://docs.python.org/zh-cn/3/library/asyncio-task.html)  
  只看前半：`coroutine`、`await`、`asyncio.run`、`gather`、`wait_for`。  
  先别深入 Future 的所有细节。

- [httpx Async 文档](https://www.python-httpx.org/async/)  
  看懂 `AsyncClient` 和 `await client.get(...)` 即可。

---

## 下一节

请打开 → [03-工程脚手架.md](03-工程脚手架.md)
