# 第1章：大模型接口与 Agent 是什么

## 本章要解决的困惑

很多资料一上来就说 Agent、ReAct、Tool Calling，初学者会晕：

- 大模型接口到底长什么样？
- Agent 和 ChatGPT 聊天有什么区别？
- 为什么还要自己写循环？

本章先把这三件事讲清楚，再进入后面的技术细节。

## 学习顺序

| 顺序 | 小节 | 目标 |
|------|------|------|
| 1 | [01-LLM-API入门.md](01-LLM-API入门.md) | 会调用（或 mock）一次对话 |
| 2 | [02-Agent概念地图.md](02-Agent概念地图.md) | 能分辨 chatbot / 工作流 / Agent |
| 3 | [03-经典范式.md](03-经典范式.md) | 知道 ReAct 在干什么（先建立图景） |

## 过关检查

- [ ] 能说出 messages 里 system/user/assistant 是干什么的
- [ ] 能运行 `python examples/stage01_llm_client_demo.py --mock`
- [ ] 能用自己的话解释：Agent 比普通聊天多了什么
- [ ] 能看懂 ReAct「思考→行动→观察」这一圈

## 课外阅读（本章读完后再看）

1. [OpenAI Text generation](https://platform.openai.com/docs/guides/text-generation)（先看 messages 概念）  
2. [Anthropic: Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)（读前半，建立「能简则简」的观念）

---

从这里开始 → [01-LLM-API入门.md](01-LLM-API入门.md)
