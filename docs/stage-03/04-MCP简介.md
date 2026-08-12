# 第3章第4节：MCP 是什么（拓展课）

## 写在前面

本节可以慢一点。  
你已经会自研工具了；MCP 是「工具生态的一种标准插头」。

没学完本节，**不影响**你继续第4章。但建议至少读完「是什么」，并完成与 `ToolRegistry` 的对照。

---

## 本节你将学会

1. MCP 想解决什么问题  
2. Host / Client / Server 是什么关系  
3. 什么时候用自研工具，什么时候用 MCP  
4. 自研 `ToolRegistry` 与 MCP Tools 概念如何一一对应  

---

## 先用一个生活例子

以前每个电器插头形状都不同，出门要带一堆转换头。  
USB 出现后，很多设备能共用一种接口。

MCP（Model Context Protocol）类似：  
让不同的「工具提供者」（文件、浏览器、数据库）用更统一的方式接到 AI 应用上。

---

## 一步一步讲清楚

### 第1步：角色

| 名称 | 人话 | 类比本仓库 |
|------|------|------------|
| Host | 你的 AI 应用（宿主） | 将来跑 `AgentLoop` 的进程 / 第10章 API |
| Client | 宿主里负责连接 MCP 的组件 | （本仓库未实现；你可想象成适配器） |
| Server | 真正提供工具/资源的进程 | 外部能力提供者 |

### 第2步：它提供什么

- Tools：可调用的动作（≈ 你的 `ToolSpec` + `execute`）  
- Resources：可读的资料（≈ 只读知识/文件句柄）  

### 第3步：和自研 ToolRegistry 的关系

| 情况 | 建议 |
|------|------|
| 学原理、写业务私有 API | 自研工具（本仓库主线） |
| 复用现成能力（本地文件等） | 可尝试 MCP Server |
| 生产 | 两者都行，但权限、审计、超时都要有 |

---

## 打开代码一起看（概念对照，无强制依赖）

打开 `src/agent_lab/tools/`（`__init__.py` / `builtin.py`）。

| MCP 概念 | 本仓库自研对应 |
|----------|----------------|
| Tool 名称 | `ToolSpec.name` |
| 描述（给模型看） | `ToolSpec.description` |
| 参数 schema | 注册时的 parameters / Pydantic |
| 调用 | `ToolRegistry.execute(...)` |
| 失败观察 | 返回 `ERROR:…` 字符串给 Loop |
| 权限 | `side_effect` + `require_confirmation` |

读官方介绍时，用上表翻译：你学的不是另一套宇宙，只是**协议标准化**了。

本章没有强制 MCP 代码依赖，避免初学环境变复杂。  
有余力再按课后链接跑官方 Python SDK 示例。

---

## 动手做

### 练习 A（必做）

用自己的话写 8 行：MCP 是什么，它不替代什么（提示：不替代你对循环与权限的理解）。

### 练习 B（必做）

把上表抄进笔记，并标出：若接入不明 MCP Server，缺了哪两道闸最危险（提示：白名单、HITL）。

### 练习 C（选做）

按官方文档跑一个示例 server。

---

## 本节小结 / 第3章收束

恭喜：你已经完成 Agent 最核心的一章。

请确认：

```powershell
python examples/stage03_tool_agent_demo.py --mock
pytest tests/test_tool_agent.py -q
```

都通过后，回 [第3章 README](README.md) 勾选过关，再进入第4章。

---

## 课后阅读

- [MCP Introduction](https://modelcontextprotocol.io/introduction)  
- [MCP Tools 概念](https://modelcontextprotocol.io/docs/concepts/tools)  
- [Python SDK](https://github.com/modelcontextprotocol/python-sdk)  

---

## 下一章

→ [../stage-04/README.md](../stage-04/README.md)
