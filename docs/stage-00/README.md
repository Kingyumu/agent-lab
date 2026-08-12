# 第0章：Python 与工程基础

## 本章为什么存在

后面写 Agent 时，你会不断处理「请求、响应、工具参数、错误」。  
如果基础写法不规范，后面每一章都会又累又乱。

所以第0章不讲 AI，只做三件事：

1. 用规范方式描述数据（类型 + Pydantic）
2. 学会异步地访问网络（Agent 天天在等网络）
3. 认清本仓库怎么组织，避免文件找不到

## 你需要什么基础

- 会写简单 Python：变量、函数、`if`、`list`/`dict`
- 会在命令行进入文件夹、运行 `python xxx.py`
- **不要求**已经会 asyncio、Pydantic、FastAPI

如果连函数都还不熟：先花 1–2 天看 [Python 官方教程](https://docs.python.org/zh-cn/3/tutorial/) 第4–5章，再回来。

## 本章学习顺序（不要乱）

| 顺序 | 小节 | 你学完应能做到 |
|------|------|----------------|
| 1 | [01-python现代写法.md](01-python现代写法.md) | 看懂并运行请求/响应模型 |
| 2 | [02-异步与HTTP.md](02-异步与HTTP.md) | 看懂并发请求示例 |
| 3 | [03-工程脚手架.md](03-工程脚手架.md) | 知道改代码该去哪个目录 |

## 学完怎么验收（过关检查）

- [ ] 能解释：什么是「类型注解」，为什么 Agent 项目喜欢用它
- [ ] 运行 `python examples/stage00_models_demo.py` 能看到「空消息被拒绝」
- [ ] 运行 `python examples/stage00_async_http_demo.py` 知道它在同时请求多个网址
- [ ] 能说出 `docs/`、`examples/`、`src/` 各自干什么

## 本章推荐课外阅读（有限，别贪多）

先只看这两份，每份看「入门部分」即可：

1. [Pydantic Models 文档](https://docs.pydantic.dev/latest/concepts/models/)：看到「Basic model usage」例程能看懂即可  
2. [asyncio 任务文档](https://docs.python.org/zh-cn/3/library/asyncio-task.html)：先看 `async def`、`await`、`asyncio.gather` 三段

---

下一节：打开 [01-python现代写法.md](01-python现代写法.md)
