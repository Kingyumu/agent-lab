# 第6章：规划、校验与人工确认

## 本章解决什么

当任务变长，只靠「边走边看」可能绕路。于是我们增加：

1. **先规划再执行**（Plan-and-Execute）
2. **出门前检查**（Verifier）
3. **关键动作停下来问人**（HITL 状态机）

## 先修

第3章循环；第2章结构化输出（规划常用 JSON）。

## 学习顺序

1. [01-规划与执行.md](01-规划与执行.md)
2. [02-反思与校验.md](02-反思与校验.md)
3. [03-图工作流与HITL.md](03-图工作流与HITL.md)

## 过关检查

- [ ] `python examples/stage06_plan_execute_demo.py --mock`
- [ ] `python examples/stage06_verifier_demo.py`
- [ ] `python examples/stage06_hitl_demo.py`
- [ ] 能说出 HITL 在真实业务里的一个例子

开始 → [01-规划与执行.md](01-规划与执行.md)
