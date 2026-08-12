# 第4章第3节：Checkpoint（断点快照）

## 写在前面

Checkpoint = 给正在运行的任务拍快照。  
进程挂了、等人审批了，都能从快照继续。

---

## 本节你将学会

1. 为什么长任务需要 checkpoint
2. 最小快照里应有哪些字段
3. 如何运行文件型 checkpoint 示例

---

## 生活例子

游戏存档。  
你不会希望打到最后一关断电后从头再来。

---

## 一步一步讲

### 第1步：什么时候需要

- 多步调研/改仓库
- 等待人工确认（HITL）
- 服务可能重启

### 第2步：最小字段

- `run_id`：这次任务编号
- `step`：走到哪一步
- `status`：running / interrupted / done
- `data`：计划、已完成项、关键 messages 等

### 第3步：教学实现

本仓库用 JSON 文件存（简单直观）。  
生产可换 Redis/SQLite/LangGraph Checkpointer，但概念相同。

---

## 打开代码一起看（逐行教材版）

打开 `src/agent_lab/runtime/checkpoint.py` 与 `examples/stage04_checkpoint_demo.py`。

### 1）快照数据结构

```python
@dataclass
class Checkpoint:
    run_id: str          # 哪一次任务
    step: int            # 走到第几步
    status: str          # running / interrupted / done ...
    data: dict[str, Any] # 业务自定义：计划、已完成、messages 等
```

`data` 故意用 dict：教学灵活；生产可换成强类型。

### 2）存到哪里

```python
self.root / f"{run_id}.json"   # 例如 .checkpoints/demo-run-1.json
```

`save`：`asdict(cp)` → `json.dumps` → 写文件。  
`load`：读文件 → `Checkpoint(**raw)`；没有文件返回 `None`。

### 3）演示在表达什么业务语义

```python
data={"plan": ["搜集资料", "写总结"], "done": ["搜集资料"]}
```

恢复后：`plan` 里不在 `done` 的就是下一步——这就是「断点续跑」的最小模型。

```powershell
python examples/stage04_checkpoint_demo.py
```

打开生成的 `.checkpoints/demo-run-1.json` 看一眼，会更直观。

### 4）和 AgentLoop 怎么接（预习）

真实接法（你可后做练习）：每执行完一步 `store.save(Checkpoint(...))`；启动时若 `load` 到 `interrupted`，从 `data` 恢复 messages/计划再继续。

---

## 动手做

1. （必做）改 `data` 里的计划，再加载，确认读到的是新内容。  
2. （必做）思考：若只存 step 数字、不存 messages，恢复时会缺什么？

---

## 小结 / 第4章收束

短期记忆管会话，长期记忆管跨会话事实，checkpoint 管任务进度。

回 [第4章 README](README.md) 做过关检查后进入第5章。

## 课后阅读

- [LangGraph Persistence](https://langchain-ai.github.io/langgraph/concepts/persistence/)

## 下一章

→ [../stage-05/README.md](../stage-05/README.md)
