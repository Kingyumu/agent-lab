# 第3章：工具调用——手写 Agent 核心（最重要）

## 先停一下，读这段

如果前面章节是「学零件」，本章就是「第一次把零件装成会动的机器」。

本章结束后，你应该能指着屏幕说：

> 看，模型先请求调用计算器，程序算完把结果塞回去，模型再给出最终答案。

请**不要跳过**。后面所有框架（LangGraph 等）都是在包装这一环。

## 你已经具备的前提（没有就先回去）

- [ ] 第0章：会跑 examples，知道 `src` 在哪
- [ ] 第1章：知道 messages 与 mock 客户端
- [ ] 第2章：知道 Prompt 与 JSON 校验的意义

## 学习顺序（严格按序）

| 顺序 | 小节 | 你将搞懂 |
|------|------|----------|
| 1 | [01-Function-Calling机制.md](01-Function-Calling机制.md) | 一次工具调用的完整报文怎么走 |
| 2 | [02-工具设计原则.md](02-工具设计原则.md) | 什么样的工具算「好工具」 |
| 3 | [03-健壮Agent-Loop.md](03-健壮Agent-Loop.md) | 循环如何避免死转、如何记录轨迹 |
| 4 | [04-MCP简介.md](04-MCP简介.md) | 拓展：工具标准化协议是什么（可稍慢） |

## 过关检查

- [ ] 能手绘：user → model(tool_calls) → 执行工具 → tool 消息 → model 最终答案
- [ ] `python examples/stage03_tool_agent_demo.py --mock` 跑通，并看到轨迹里有 `calculator`
- [ ] `pytest tests/test_tool_agent.py -q` 通过
- [ ] 能解释 `max_steps` 为什么必要

## 本章主演示命令

```powershell
python examples/stage03_tool_agent_demo.py --mock
pytest tests/test_tool_agent.py -q
```

从这里开始 → [01-Function-Calling机制.md](01-Function-Calling机制.md)
