# 第3章第3节：让 Agent Loop 更健壮

## 写在前面

课堂 Demo 能跑通，不代表它能上真实任务。  
真实世界里：工具会失败、模型会死循环、结果会特别长。

本节教你给循环装「刹车和仪表盘」。

---

## 本节你将学会

1. 为什么要有 `max_steps`
2. 工具失败时应该怎么办
3. 什么是轨迹（trace），为什么要打印/保存

---

## 先用一个生活例子

导航软件如果永远「重新规划」停不下来，你会没电。  
所以要有：

- 最多尝试次数
- 失败提示
- 行程记录（方便回放：刚才到底怎么走的）

Agent 同样需要。

---

## 一步一步讲清楚

### 第1步：最大步数

```python
for step in range(1, max_steps + 1):
    ...
```

防止模型反复调用工具却不到终点。

### 第2步：工具异常 → 变成观察文本

不要让异常直接打断整个服务。  
返回类似：

```text
ERROR: ValueError: expression 不能为空
```

模型有机会改参数再试。

### 第3步：结果截断

网页内容可能很长，全塞进 messages 会又贵又乱。  
本仓库用 `_truncate` 截断。

### 第4步：轨迹

每一步记录：

- 模型说了什么 / 申请了什么工具
- 工具返回了什么

示例脚本会打印轨迹。第9章会升级成正式评测与 tracing。

### 第5步：还可以加的刹车（了解即可）

- 全局超时
- 费用预算
- 发现「同一工具同一参数连打两次」就停止

---

## 打开代码一起看（对照行号读）

打开 `src/agent_lab/agent/loop.py` 与 `src/agent_lab/tools/__init__.py`，按「刹车 / 失败 / 截断 / 轨迹」四条线找代码。

### 1）刹车：`max_steps`

```python
for step in range(1, self.max_steps + 1):
    ...
# 若循环正常结束还没 return：
reply = f"已达到最大步数 {self.max_steps}，停止。"
return AgentRunResult(reply=reply, steps=traces, messages=messages)
```

练习时把示例里的 `max_steps=6` 改成 `1`：往往只能完成「申请工具+执行」，来不及第二轮「说最终答案」，就会走到上面这句。

### 2）失败不变成进程崩溃：`ToolRegistry.execute`

工具里 `raise ValueError(...)` 时，`execute` 捕获后返回：

```text
ERROR: ValueError: ...
```

Loop 仍然把它当 `obs` 塞进 `role=tool` 消息。  
下一轮模型（或 mock）还能继续说话——这就是「失败可观察」。

### 3）截断：`_truncate(obs)`

```python
obs = await self.registry.execute(...)
obs = _truncate(obs)   # 默认超过约 4000 字符就砍掉并加 ...[truncated]...
```

防止 `http_get` 一类工具把整页 HTML 灌进上下文。

### 4）轨迹：`StepTrace`

有工具时：

```python
traces.append(StepTrace(
    step=step,
    assistant_content=result.content,
    tool_calls=result.tool_calls,
    observations=observations,  # 如 ["calculator: 16"]
))
```

无工具（最终答案）时也会 append 一步，方便完整回放。  
`examples/stage03_tool_agent_demo.py` 打印的就是 `result.steps`。

运行：

```powershell
python examples/stage03_tool_agent_demo.py --mock
```

---

## 动手做

### 练习 A（必做）

把 `max_steps=1` 再跑 mock 计算器任务，观察是否会「没来得及给最终答案就停」。  
理解：步数太小会截断任务。

（改完练习后改回合理值，如 6。）

### 练习 B（必做）

在笔记写：若工具返回 ERROR，下一轮模型可能怎么做？

---

## 常见卡点问答

**Q：达到最大步数算成功吗？**  
A：通常算未完成。应提示用户或降级策略，不要假装成功。

---

## 本节小结

- 循环必须能停
- 失败要可回传
- 轨迹是排障的眼睛

---

## 课后阅读

- [LangGraph Agentic Concepts](https://langchain-ai.github.io/langgraph/concepts/agentic_concepts/)：对照理解循环与终止（先浏览）  
- [asyncio 超时](https://docs.python.org/zh-cn/3/library/asyncio-task.html#timeouts)

---

## 下一节

→ [04-MCP简介.md](04-MCP简介.md)
