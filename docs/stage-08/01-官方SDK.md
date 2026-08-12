# 第8章第1节：官方 SDK 为什么还要学

## 写在前面

框架会变，Chat Completions / Tool Calling 协议相对稳定。  
本仓库的 `OpenAICompatClient` 就是对官方 SDK 的薄封装——读懂它，等于读懂生产里最薄的一层。

## 本节你将学会

1. 官方 SDK 在本仓库落在哪一行  
2. tools / stream / timeout 如何传到 `chat.completions.create`  
3. 第3章 AgentLoop 依赖了 SDK 的哪些能力  

## 你要精读的点（对照官方文档目录）

1. tools / tool_choice  
2. 并行 tool_calls  
3. stream  
4. usage（花了多少 token）  
5. 429 限流重试  

---

## 打开代码一起看（对照自研封装）

打开 `src/agent_lab/llm/__init__.py` 的 `OpenAICompatClient`（若拆到了 `client.py` 则打开实际定义处）。

### 1）SDK 在哪一层

```python
from openai import AsyncOpenAI
self._client = AsyncOpenAI(api_key=..., base_url=..., timeout=...)
```

你平时写的 `await client.chat(messages, tools=...)` 最终都落到：

```python
await self._client.chat.completions.create(**kwargs)
```

`base_url` 可换兼容网关；协议仍按 OpenAI Chat Completions。

### 2）messages 如何装箱

自研 `ChatMessage` → SDK 要的 `dict`（role / content / tool_calls…）。  
AgentLoop 只认识自研类型；封装层负责翻译——这是「薄封装」的价值。

### 3）tools 如何交给官方接口

```python
if tools:
    kwargs["tools"] = tools
    kwargs["tool_choice"] = "auto"
```

与 OpenAI Function Calling 文档一致。  
第3章 Loop 依赖：这里必须能传 tools，且响应里能解析 `tool_calls`。

### 4）流式在哪

`chat_stream`：`stream=True`，然后：

```python
async for event in stream:
    if event.choices[0].delta.content:
        yield delta.content
```

第1章可跳过；做聊天 UI / 打字机效果时再启用。  
注意：带 tools 的流式协议更绕，初学先用非流式 Loop。

### 5）timeout 与错误

构造客户端时传入 `timeout`，避免工具环一路卡死。  
生产还应：识别 429、指数退避重试、记录 `usage`。

### 6）练习对照：Loop 依赖清单

把第3章 `AgentLoop` 依赖的能力勾掉：

| 能力 | 没有会发生什么 |
|------|----------------|
| `chat` | 无法对话 |
| 传入 `tools` | 模型不会结构化调工具 |
| 解析 `tool_calls` | 循环无法「行动」 |
| 回填 tool 角色消息 | 模型看不到观察 |
| （可选）stream | 仅影响体验 |
| （可选）usage | 不影响正确性，影响成本治理 |

少了前四项，Loop 都跑不起来——所以「会框架」之前必须会这层。

```powershell
python examples/stage01_llm_client_demo.py --mock
python examples/stage03_tool_agent_demo.py --mock
```

---

## 动手做

1. （必做）对照第3章 AgentLoop，列出它依赖了 SDK 的哪些能力（可抄上表后用自己的话改写）。  
2. （选做）在笔记画：`AgentLoop` → `OpenAICompatClient.chat` → `AsyncOpenAI.chat.completions.create` 三层箭头。

## 课后阅读

- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling)  
- [openai-python](https://github.com/openai/openai-python)

## 下一节

→ [02-LangGraph入门.md](02-LangGraph入门.md)
