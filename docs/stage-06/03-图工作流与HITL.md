# 第6章第3节：状态机与人工确认（HITL）

## 写在前面

HITL = Human-in-the-loop：关键步骤停住，等人点头再继续。  
手写状态机先把「允许哪些转移」学清楚，第8章再用 LangGraph interrupt。

## 生活例子

发公告：写稿 → 主编审 → 通过才发布；退回就修改再审。

## 一步一步讲

```text
generate --generated--> review --approve--> publish --published--> done
                         | reject
                         v
                       revise --revised--> review
任意状态 --cancel--> cancelled
```

---

## 打开代码一起看（逐行教材版）

打开 `src/agent_lab/planning/hitl_flow.py` 与 `examples/stage06_hitl_demo.py`。

### 1）状态长什么样

```python
Status = Literal["generate", "review", "revise", "publish", "cancelled", "done"]

@dataclass
class HitlState:
    status: Status = "generate"
    draft: str = ""
    review_note: str = ""
```

### 2）`next_state`：只允许合法转移

每一条 `if` 都是一条「边」：

```python
if state.status == "generate" and event == "generated":
    return HitlState(status="review", draft=payload)
if state.status == "review" and event == "approve":
    return HitlState(status="publish", draft=state.draft, review_note=payload)
...
if event == "cancel":
    return HitlState(status="cancelled", draft=state.draft, review_note=payload)
raise ValueError(f"非法转移: status={state.status}, event={event}")
```

非法组合（例如还在 `generate` 就 `approve`）会直接报错——这是故意的，防止流程乱跳。

### 3）演示脚本在走哪条路径

```powershell
python examples/stage06_hitl_demo.py
```

路径：生成 → 驳回 → 修订 → 通过 → 发布 → done。

### 4）和 Checkpoint 的关系

`review` 状态最适合落盘 checkpoint（`status=interrupted`），等人工事件到来再 `next_state`。

---

## 动手做

1. （必做）读源码确认：任意状态 `cancel` 都能到 `cancelled`。  
2. （选做）故意调用非法转移，观察 `ValueError`。

## 小结 / 第6章收束

规划管长任务，校验管质量，HITL 管风险。

## 课后阅读

- [LangGraph Human-in-the-loop](https://langchain-ai.github.io/langgraph/concepts/human_in_the_loop/)

## 下一章

→ [../stage-07/README.md](../stage-07/README.md)
