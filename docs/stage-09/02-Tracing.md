# 第9章第2节：Tracing（把过程录下来）

## 写在前面

评测告诉你「过没过」；Tracing 告诉你「为什么过/不过」。  
没有轨迹，线上翻车只能猜。

## 生活例子

监控录像。出了事回放：谁进门、拿了什么、何时离开。  
Agent 的录像就是 trace：每一步 LLM / 工具 / 检索的输入输出与耗时。

## 本节你将学会

1. 最小自研 trace 字段长什么样  
2. 本仓库 `StepTrace` 已经记了什么、还缺什么  
3. 何时再接 Langfuse 等平台  

---

## 打开代码一起看（对照 AgentLoop）

打开 `src/agent_lab/agent/loop.py`。

### 1）已有的 `StepTrace`

```python
@dataclass
class StepTrace:
    step: int
    assistant_content: str | None
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    observations: list[str] = field(default_factory=list)
```

| 字段 | 人话 |
|------|------|
| `step` | 第几轮循环 |
| `assistant_content` | 模型本轮文本（最终回答时常在这里） |
| `tool_calls` | 本轮要执行的工具名+参数 |
| `observations` | 工具返回的观察文本（含 `ERROR:…`） |

`AgentRunResult.steps` 就是一次运行的完整「录像带」。

### 2）它还缺什么（生产常加）

| 字段 | 为什么要 |
|------|----------|
| `run_id` / `session_id` | 把多步串成一次运行、跨请求查询 |
| `latency_ms` | 找慢在 LLM 还是工具 |
| `model` / `token_usage` | 成本与排障 |
| `error` | 区分业务失败与异常 |
| `type` | `llm` / `tool` / `retrieve` |

落盘时一行 JSON 即可：

```json
{"run_id":"...","step":1,"type":"tool","name":"calculator","latency_ms":12,"ok":true}
```

写到 `logs/*.jsonl` 就能开箱。

### 3）和评测怎么配合

```text
题集失败
  → 查该次 run 的 steps：第几步开始跑偏
  → 是没调工具？工具 ERROR？最终话术缺关键字？
  → 改 Prompt / 工具描述 / max_steps
  → 重跑评测
```

### 4）平台（有余力再接）

Langfuse / Phoenix / LangSmith / OpenTelemetry。  
原则：**先有自研字段语义，再映射到平台**，不会被厂商绑死概念。

---

## 动手做

1. （必做）列出 AgentLoop 每一步你想记录的 6 个字段。  
2. （选做）给循环加 `latency_ms`，用 `time.perf_counter()` 填上后打印。

## 小结 / 第9章收束

评测证明好坏，轨迹解释好坏。两者一起，才谈得上「可迭代」。

## 课后阅读

- [Langfuse Get Started](https://langfuse.com/docs/get-started)

## 下一章

→ [../stage-10/README.md](../stage-10/README.md)
