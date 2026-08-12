# agent-lab

Python AI Agent **教材型**实验仓库：按章节循序渐进。每节有生活例子、逐步讲解、对照代码、练习与小结。

如果你以前只写过普通 Python、还没做过 Agent，请从本文件开始，**按顺序往下学，不要跳章**。

## 学完能做什么

做出一个「会调用工具、能查资料、能多轮对话」的 AI Agent，并清楚它内部每一步在干什么。

学习台阶（务必按序）：

```text
第0章  Python 工程基础
  ↓
第1章  会调用大模型
  ↓
第2章  提示词与结构化输出
  ↓
第3章  手写 Agent 核心循环（最重要）
  ↓
第4章  记忆
  ↓
第5章  RAG
  ↓
第6章  规划 / 校验 / 人工确认
  ↓
第7章  多 Agent
  ↓
第8章  框架（LangGraph）
  ↓
第9章  评测与排错
  ↓
第10章 FastAPI 服务化
```

**为什么不能先学第8章框架？**  
框架把关键循环藏起来了。没亲手写过第3章，后面报错会很难排查。本仓库坚持：先手写，再框架。

## 每章怎么读（固定四步）

1. **先读文字**（生活例子 + 逐步讲解），读到「打开代码一起看」再停  
2. **再跑示例**（文档里的命令）  
3. **对照输出**，和文字解释对上号  
4. **做本节练习**（至少第1题），再进下一节  

一章读完，看该章 README 末尾的「过关检查」。全勾了再进下一章。

阅读约定：

- **加粗词**多为正式术语，后面会反复出现  
- 「先记住结论」：先接受，后文再展开  
- 「先别改代码」：先按演示跑通再改  
- 卡住超过 30 分钟：看该节「常见卡点」，或重跑示例对比  

## 安装（只需一次）

```powershell
cd agent-lab
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

以后每次学习先激活虚拟环境：

```powershell
.\.venv\Scripts\Activate.ps1
```

**现在先不要申请 API Key。** 多数示例加 `--mock` 即可学流程。等学到第1章末尾再配置 `.env`。

冒烟检查：

```powershell
python examples/stage00_models_demo.py
python examples/stage03_tool_agent_demo.py --mock
pytest -q
```

## 目录说明

| 路径 | 用途 |
|------|------|
| `docs/` | 教材正文（按章阅读） |
| `examples/` | 可运行演示 |
| `src/agent_lab/` | 可复用实现 |
| `prompts/` | 提示词文稿 |
| `evals/` | 评测数据与脚本 |
| `tests/` | 单元测试 |

```text
agent-lab/
├── README.md          # 本文件（入口）
├── pyproject.toml
├── docs/
├── examples/
├── src/agent_lab/
├── prompts/
├── evals/
└── tests/
```

## 章节入口

从 **第0章** 开始，不要先跳到第3章或框架。

| 章 | 标题 | 大约多久 | 入口 |
|----|------|----------|------|
| 0 | Python 与工程基础 | 3–5 天 | [docs/stage-00/README.md](docs/stage-00/README.md) |
| 1 | 大模型与 Agent | 2–4 天 | [docs/stage-01/README.md](docs/stage-01/README.md) |
| 2 | 提示词与结构化输出 | 3–5 天 | [docs/stage-02/README.md](docs/stage-02/README.md) |
| 3 | 手写 Tool Agent（核心） | 5–8 天 | [docs/stage-03/README.md](docs/stage-03/README.md) |
| 4 | 记忆与 Checkpoint | 3–5 天 | [docs/stage-04/README.md](docs/stage-04/README.md) |
| 5 | RAG | 4–7 天 | [docs/stage-05/README.md](docs/stage-05/README.md) |
| 6 | 规划 / 校验 / HITL | 3–5 天 | [docs/stage-06/README.md](docs/stage-06/README.md) |
| 7 | 多 Agent | 3–5 天 | [docs/stage-07/README.md](docs/stage-07/README.md) |
| 8 | 框架实战 LangGraph | 4–7 天 | [docs/stage-08/README.md](docs/stage-08/README.md) |
| 9 | 评测与可观测 | 3–5 天 | [docs/stage-09/README.md](docs/stage-09/README.md) |
| 10 | 服务化 | 3–5 天 | [docs/stage-10/README.md](docs/stage-10/README.md) |

下一页 → [第0章导读](docs/stage-00/README.md) → [0.1 Python 现代写法](docs/stage-00/01-python现代写法.md)
