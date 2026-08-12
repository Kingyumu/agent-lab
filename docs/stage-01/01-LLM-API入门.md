# 第1章第1节：大模型 API 入门

## 写在前面

把「大模型」先当成一个**远程函数**：

- 你输入：一段对话记录（messages）
- 它输出：助手的下一句话

Agent 后面所有花活，都建立在这个最基本的调用之上。

---

## 本节你将学会

1. messages（消息列表）是怎么组成的
2. 什么是 system / user / assistant
3. 如何运行本仓库的 LLM 客户端（可先 mock）

---

## 先用一个生活例子

你和客服通话：

```text
系统设定：你是银行客服，回答要礼貌（system）
客户：我要查余额（user）
客服：请提供卡号后四位（assistant）
客户：1234（user）
客服：您的余额是…（assistant）
```

大模型 API 几乎就是在传输这样一份「通话记录」，然后请模型续写下一句客服的话。

---

## 一步一步讲清楚

### 第1步：一次调用最小长这样

```python
messages = [
  {"role": "system", "content": "你是简洁的助手"},
  {"role": "user", "content": "用一句话解释什么是 Agent"},
]
# 调用后得到 assistant 的 content
```

### 第2步：三个角色分别干什么

| 角色 | 谁写的 | 作用 |
|------|--------|------|
| system | 你（开发者） | 规定规则、人设、边界 |
| user | 用户 | 提出问题/指令 |
| assistant | 模型 | 模型的回答（后面还会带 tool 请求） |

初学先记住：  
**system 定规矩，user 提需求，assistant 给回复。**

### 第3步：几个常见旋钮（先认识，不深挖）

| 参数 | 人话 | 初学建议 |
|------|------|----------|
| model | 用哪个模型 | 先用小模型或 mock |
| temperature | 回答随机程度 | Agent 场景常用偏低（更稳） |
| max_tokens | 最多生成多长 | 防止回答太长 |
| stream | 是否边生成边返回 | 做聊天窗体验时再开 |

### 第4步：什么是 mock（本教材很重要）

没有 API Key 时，仓库提供 `MockLLMClient`：  
它不联网，用规则假装模型在回答。

这样你可以：

- 先学「调用方式、程序结构」
- 不花钱、不等网络
- 后面第3章也能先把 Agent 循环跑通

### 第5步：真实 Key 以后怎么配（先看不做也行）

1. 复制 `.env.example` → `.env`
2. 填写 `OPENAI_API_KEY`
3. 如使用兼容网关，改 `OPENAI_BASE_URL`
4. 运行示例时去掉 `--mock`

---

## 打开代码一起看（逐行教材版）

> 说明：逻辑写在 `src/agent_lab/llm/__init__.py`。  
> `llm/client.py` 只是再导出，方便 `from agent_lab.llm.client import ...`，**不要以为 client.py 里还有另一套实现**。

---

### A. 演示脚本：`examples/stage01_llm_client_demo.py`

```python
async def main(mock: bool) -> None:
    client = build_default_client(mock=mock)   # ① 选真客户端还是 Mock
    messages = [
        ChatMessage(role="system", content="你是简洁的助手。"),
        ChatMessage(role="user", content="用一句话介绍什么是 AI Agent。"),
    ]
    result = await client.chat(messages)       # ② 发对话，等回复
    print("回复:", result.content)             # ③ 打印文字答案
```

人话：

1. `build_default_client(mock=True)` → 一定用假模型  
2. `mock=False` 且 `.env` 里有 Key → 用真 API  
3. `await client.chat(messages)` → 把通话记录交给模型，拿回 `ChatResult`

末尾 `asyncio.run(main(...))`：和第0章一样，启动异步入口。

---

### B. `ChatMessage`：一条消息长什么样

```python
@dataclass
class ChatMessage:
    role: str
    content: str | None = None
    tool_call_id: str | None = None   # 第3章：工具结果要带回这个 id
    name: str | None = None
    tool_calls: list[dict[str, Any]] | None = None  # 第3章：模型申请调工具

    def to_openai(self) -> dict[str, Any]:
        # 转成 OpenAI API 要的字典；没有的字段就不塞进去
        ...
```

初学先盯住：`role` + `content`。  
`tool_calls` / `tool_call_id` 第3章才会真正用到——现在知道「预留了位置」即可。

`ChatResult` 则是一次调用的返回：`content`（最终话）+ `tool_calls`（要不要调工具）。

---

### C. `OpenAICompatClient.chat`：真请求在干什么

核心三步：

```text
1. messages 转成 API 字典： [m.to_openai() for m in messages]
2. 若传了 tools，一并放进请求（第3章用）
3. await ...chat.completions.create(...)
4. 把返回整理成 ChatResult（文字 + 可选 tool_calls）
```

对应代码大意：

```python
kwargs = {
    "model": self.model,
    "messages": [m.to_openai() for m in messages],
    "temperature": temperature,
}
if tools:
    kwargs["tools"] = tools
    kwargs["tool_choice"] = "auto"
resp = await self._client.chat.completions.create(**kwargs)
```

`chat_stream` 则是边生成边 `yield` 文字片段；第1章可先跳过。

---

### D. `MockLLMClient`：没 Key 时怎么假装模型

两种模式：

1. **脚本模式**：构造时传入 `script=[ChatResult(...), ...]`，每次 `chat` 按顺序吐下一条（第2、3章演示常用）  
2. **规则模式**（默认）：
   - 用户话里有「算/计算/+/*」且给了 tools → 假装要调 `calculator`
   - messages 里已有 `role=tool` → 假装根据工具结果说话
   - 否则 → 回 `(mock) 收到：...`

所以你现在跑 `--mock`，会看到「收到：…」；到第3章带工具时，mock 才会「申请计算器」。

---

### E. `build_default_client`

```python
def build_default_client(*, mock: bool = False):
    if mock or not settings.has_api_key:
        return MockLLMClient()
    return OpenAICompatClient()
```

一张开关表：

| 条件 | 得到谁 |
|------|--------|
| `--mock` | Mock |
| 没有有效 Key | Mock |
| 有 Key 且不 mock | 真客户端 |

---

### F. 运行

```powershell
python examples/stage01_llm_client_demo.py --mock
```

期望：打印 `(mock) 收到：用一句话介绍什么是 AI Agent。` 一类回复。

---

## 动手做

### 练习 A（必做）

改示例里的用户问题，换成你自己的一句话，再运行 `--mock`，确认输出跟着变。

### 练习 B（必做）

在笔记里用自己的话写：system 消息和 user 消息的区别。

### 练习 C（选做，需 Key）

对比 temperature=`0` 与 `1` 对同一问题的差异。

---

## 常见卡点问答

**Q：报认证错误 / 401？**  
A：Key 无效或没读到 `.env`。先用 `--mock` 继续学。

**Q：stream 是什么？**  
A：边生成边返回。第1章先会非流式即可。

---

## 本节小结

- 调大模型 = 提交 messages，拿回 assistant 消息
- 先 mock 学流程，再上真实 Key
- 后面 Agent 只是在 messages 上反复追加内容

---

## 课后阅读

- [OpenAI Text generation](https://platform.openai.com/docs/guides/text-generation)：重点看 messages  
- [OpenAI Python SDK](https://github.com/openai/openai-python)：看最小调用例子

---

## 下一节

→ [02-Agent概念地图.md](02-Agent概念地图.md)
