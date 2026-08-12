# 第0章第1节：Python 现代写法（类型与 Pydantic）

## 写在前面

本节不教 AI。  
我们先学会一件以后天天用的事：**把「乱七八糟的字典」变成「有规则的数据」**。

请按标题顺序读，读到「打开代码一起看」再运行命令。

---

## 本节你将学会

1. 什么是类型注解，看一行代码就能知道参数该是什么
2. 什么是 Pydantic，为什么比普通 `dict` 更适合 Agent
3. 如何运行本仓库的第一个示例，并看懂输出

---

## 先用一个生活例子

想象你在奶茶店点单。

不好的方式：客人随便说一串话，店员自己猜。

```text
"嗯那个……来一杯，别太甜，杯子写小明"
```

好的方式：点单系统有固定字段：

```text
姓名：小明
甜度：少糖
温度：冰
```

字段不对（比如姓名空着），系统直接拒绝，不做到一半才发现错。

在 Agent 项目里：

- 用户消息、工具参数、最终回复，都像「点单字段」
- **Pydantic 模型**就是点单系统的表格
- **类型注解**是表格上印着的「姓名必须是文字、数量必须是数字」

---

## 一步一步讲清楚

### 第1步：没有类型时，错得很晚

```python
def greet(name, times):
    return (name + "!") * times
```

别人可能传入 `greet(3, "小明")`，要运行到这一行才报错，而且错误难读。

### 第2步：加上类型注解

```python
def greet(name: str, times: int) -> str:
    return (name + "!") * times
```

这行的意思是：

- `name` 应该是字符串 `str`
- `times` 应该是整数 `int`
- 函数返回值也应该是字符串

类型注解**不会在运行时强制拦你**（普通 Python 如此），但它能：

- 让编辑器/检查器提前标红
- 让读代码的人（包括未来的你）秒懂
- 为下一步「Pydantic 真正校验」做准备

你以后会常见：

| 写法 | 人话 |
|------|------|
| `str` | 一段文字 |
| `int` | 整数 |
| `str \| None` | 可以是文字，也可以是空（没有） |
| `list[str]` | 一串文字的列表 |
| `dict[str, Any]` | 键是文字、值随便的字典 |

### 第3步：Pydantic 真正在运行时检查

普通字典：

```python
req = {"session_id": "s1", "message": "   "}  # 空消息，字典照样收
```

Pydantic 模型会在创建对象时检查规则。本仓库的请求模型大意是：

- 必须有 `session_id`
- `message` 不能为空
- 会自动去掉首尾空格

所以空消息会在**入口**被拒绝，不会进到 Agent 后半程才炸。

### 第4步：为什么 Agent 特别需要这个

Agent 运行时会不断出现这类数据：

- 用户刚说了什么
- 模型要求调用哪个工具、参数是什么
- 工具返回了什么
- 最终怎么回复用户

如果全用 `dict`，字段名会越写越乱（`msg` / `message` / `text` 混用），错误极难查。  
**先把数据结构定清楚，再写 Agent 循环**——这是本教材的第一条工程原则。

---

## 打开代码一起看（对照源码）

打开 `src/agent_lab/models.py` 与 `examples/stage00_models_demo.py`。

### 1）`RunStatus`：有限几个合法状态

```python
class RunStatus(str, Enum):
    pending = "pending"
    running = "running"
    succeeded = "succeeded"
    ...
```

用枚举而不是随便写字符串，避免出现 `"sucess"` 这种拼写漏洞。

### 2）`AgentRequest`：进门安检

```python
session_id: str = Field(..., min_length=1)
message: str = Field(..., min_length=1, max_length=20_000)

@field_validator("message")
def strip_message(cls, v: str) -> str:
    v = v.strip()
    if not v:
        raise ValueError("message 不能为空")
    return v
```

- `...` 表示必填  
- `strip` 后再判空：纯空格也不算有效消息  

### 3）`AgentResponse`：出门固定形状

必有 `session_id`、`reply`；可选带上 `tool_calls` 记录；`status` 默认成功。

### 4）演示在验证什么

```powershell
python examples/stage00_models_demo.py
```

1. 正常创建（message 会被 strip）  
2. 正常响应  
3. 空 message → `ValidationError`（入口拦住）

```powershell
pytest tests/test_models.py -q
```

---

## 动手做（按顺序）

### 练习 A（必做，5 分钟）

故意改 `examples/stage00_models_demo.py`，再创建一个：

- `session_id="demo"`
- `message="你好"`

并 `print` 出来。改完运行，确认你改的代码真的执行了。

### 练习 B（必做，15 分钟）

打开 `src/agent_lab/models.py`，给 `AgentRequest` 增加字段：

```python
max_steps: int = Field(default=8, ge=1, le=30)
```

含义：默认最多 8 步，且必须在 1～30。  
然后在示例里打印 `req.max_steps`。

### 练习 C（选做）

自己新建一个模型 `PlanStep`，字段：

- `id: str`
- `title: str`
- `depends_on: list[str] = []`

写 3 行代码创建它并打印。

---

## 常见卡点问答

**Q：类型注解是不是必须写？**  
A：对本教材，是的。后面工具参数、结构化输出都靠它降低混乱。

**Q：Pydantic 和 dict 选哪个？**  
A：进出边界（用户输入、模型 JSON、API 响应）用 Pydantic；函数内部临时小数据可以用 dict，但不要让 dict 满天飞。

**Q：报错英文看不懂怎么办？**  
A：先看 `ValidationError` 下面指出的字段名（比如 `message`），再看 `input_value` 你传了什么。

---

## 本节小结

- 类型注解 = 给参数「贴标签」，方便人和工具阅读
- Pydantic = 在运行时按规则检查数据
- Agent 项目里，先定数据形状，再写复杂逻辑

---

## 课后阅读（怎么读）

只读这一页，不要整站乱点：

- [Pydantic：Models](https://docs.pydantic.dev/latest/concepts/models/)  
  阅读目标：看懂官方第一个 `class User(BaseModel)` 例子，知道 `User(name=..., age=...)` 会校验。

---

## 下一节

请打开 → [02-异步与HTTP.md](02-异步与HTTP.md)
