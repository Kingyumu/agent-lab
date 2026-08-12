# 第3章第1节：Function Calling 机制（一圈走完）

## 写在前面

本节是全书最关键的一节之一。  
我们用「算 `(3+5)*2`」这件小事，把 Agent 的核心闭环走一遍。

请慢读。读完再运行示例。

---

## 本节你将学会

1. 什么是工具（Tool）
2. 模型如何提出「我要调用某某工具」
3. 程序如何执行工具，并把结果返回模型
4. 最终答案如何产生

---

## 先用一个生活例子

你不会心算也可能找计算器。

```text
你：算一下 (3+5)*2
助手心里：我该用计算器
助手按下：(3+5)*2
计算器显示：16
助手开口：结果是 16
```

Function Calling 就是让模型用**结构化方式**说「我要按计算器」，而不是在散文里暗示。

---

## 一步一步讲清楚

### 第1步：先告诉模型「你有哪些工具」

程序会把工具说明书（schema）发给模型，例如：

- 工具名：`calculator`
- 干什么：算算术表达式
- 参数：`expression`（字符串）

模型不是魔法变出工具，它只能申请调用你提供的那些。

### 第2步：模型可能不直接给最终答案

它可能返回类似：

```text
tool_calls = [
  {
    "id": "call_1",
    "function": {
      "name": "calculator",
      "arguments": "{\"expression\": \"(3+5)*2\"}"
    }
  }
]
```

注意：`arguments` 常常是**字符串形式的 JSON**，程序要用 `json.loads` 解析。

### 第3步：程序本地执行真正的函数

```text
name = calculator
args = {"expression": "(3+5)*2"}
result = "16"
```

这一步是你的 Python 代码在跑，不是模型在跑。

### 第4步：把结果作为 role=tool 的消息追加回去

```text
messages 追加一条：
role: tool
tool_call_id: call_1
content: 16
```

### 第5步：再次调用模型

模型看到工具结果后，才生成最终对用户说的话：

```text
结果是 16。
```

### 第6步：串起来就是 Agent Loop

```text
循环：
  问模型
  如果有 tool_calls：
      执行每个工具
      把结果追加进 messages
      继续循环
  否则：
      把 content 当最终答案，结束
```

---

## 打开代码一起看（逐行教材版）

请同时打开这四个文件，按下面顺序读：

1. `tools/__init__.py`（工具怎么登记、怎么执行）  
2. `tools/builtin.py`（计算器真正算什么）  
3. `agent/loop.py`（主循环）  
4. `examples/stage03_tool_agent_demo.py`（怎么组装起来跑）

---

### A. 工具说明书 → 发给模型的 schema

`ToolSpec` = 你自己用的说明书（含副作用、是否要确认）。  
`Tool.openai_schema()` = 发给模型的精简版：

```python
{
  "type": "function",
  "function": {
    "name": "...",
    "description": "...",   # 模型靠这段决定「要不要用我」
    "parameters": { ... }    # JSON Schema：参数长什么样
  }
}
```

`ToolRegistry.list_schemas()`：把所有已注册工具的 schema 列成一张单子，交给 `client.chat(..., tools=schemas)`。

---

### B. `ToolRegistry.execute`：执行一次工具调用

模型给的是**字符串参数**，不是 Python dict：

```python
arguments_json = '{"expression": "(3+5)*2"}'
```

`execute` 做的事：

```text
按 name 找到 Tool
  → 若需要确认且未确认：返回 ERROR 字符串（不真执行）
  → json.loads(arguments_json) 得到 dict
  → 调用 handler(args)（同步或 async 都能接）
  → 成功：return str(结果)
  → 异常：return "ERROR: ..."   ← 注意：不往外抛死，好让 Agent 继续聊
```

这就是「工具失败变成观察」的代码落点。

---

### C. `calculator`：为什么不用 `eval`

`builtin.py` 里用 `ast` 只允许数字和 `+ - * / **`。  
这样模型就算传来奇怪字符串，也不会变成「执行任意代码」。

---

### D. `AgentLoop.run`：心脏循环（对照着看）

**初始化 messages：**

```python
messages = [
    ChatMessage(role="system", content=self.system_prompt),  # 常来自 prompts/react_agent.txt
    ChatMessage(role="user", content=user_message),
]
schemas = self.registry.list_schemas()
```

**每一圈：**

```python
result = await self.client.chat(messages, tools=schemas)

# 情况1：模型不再要工具 → 这就是最终答案
if not result.tool_calls:
    return AgentRunResult(reply=result.content or "", ...)

# 情况2：模型要调工具
messages.append(assistant带tool_calls的消息)
for call in result.tool_calls:
    obs = await self.registry.execute(name, arguments字符串)
    obs = _truncate(obs)          # 防止观察太长撑爆上下文
    messages.append(role=tool 的消息，带上 tool_call_id)
# 然后 for 继续下一圈，再问模型
```

**刹车：** `for step in range(1, max_steps+1)`，圈数用完仍没最终答案 → 返回「已达到最大步数…」。

**仪表盘：** 每一步 `traces.append(StepTrace(...))`，示例脚本会打印出来，方便你对照。

---

### E. 演示脚本如何串起来

```python
client = build_default_client(mock=mock)
agent = AgentLoop(client, build_builtin_registry(), max_steps=6)
result = await agent.run("请计算 (3+5)*2，并告诉我结果。")
```

`--mock` 时：`MockLLMClient` 看到「算」会先返回 calculator 的 `tool_calls`；  
Loop 执行工具得到 `16`；下一轮 mock 看到 tool 消息，再返回最终话。

运行并对照轨迹：

```powershell
python examples/stage03_tool_agent_demo.py --mock
pytest tests/test_tool_agent.py -q
```

请在输出里确认：先有 `calculator: 16`，再有最终回答。

---

## 动手做

### 练习 A（必做）

在纸上按时间顺序写 5 行（用中文）：  
用户说了什么 → 模型申请了什么 → 程序算了什么 → 回传了什么 → 最终说了什么。

### 练习 B（必做）

把问题改成「现在几点？（UTC）」类需求，先阅读 `get_time` 工具；若用 mock，可能不会自动调用时间工具（mock 规则偏计算）。  
有真实 Key 后可试真实模型是否选择 `get_time`。

### 练习 C（选做）

给 registry 再注册一个超简单工具 `echo`，返回参数里的 `text`。观察 schema 增加后列表变化。

---

## 常见卡点问答

**Q：为什么不让模型直接心算？**  
A：可以，但不稳。工具让关键动作可验证、可替换、可加权限。

**Q：一次返回多个 tool_calls 怎么办？**  
A：按列表逐个（或并行）执行，每个结果都用对应 `tool_call_id` 回传。

**Q：mock 和真模型行为不一致？**  
A：正常。mock 用来学协议与代码路径；真模型用来学「选择工具」的质量。

---

## 本节小结

- Function Calling = 模型申请工具 + 程序执行 + 结果回灌 + 再生成
- 你已经触摸到 Agent 的心脏

---

## 课后阅读（本节后精读）

- [OpenAI Function Calling 指南](https://platform.openai.com/docs/guides/function-calling)  
  阅读目标：看懂官方「tools → tool_calls → tool message」示例，和本仓库对照。

---

## 下一节

→ [02-工具设计原则.md](02-工具设计原则.md)
