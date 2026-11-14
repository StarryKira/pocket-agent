# 01｜20 行代码的 Agent，为什么开了 15 个分身？

视频：（发布后补链接）

照抄 Agent SDK 官方入门教程，只把模型换成 DeepSeek，让它修 `utils.py` 里的两个 bug。第一次它派了 15 个子 Agent，快 4 分钟一行没改；加 4 行配置之后，几秒到几十秒就修完了。

## 文件

| 文件 | 说明 |
|---|---|
| `agent.py` | 最终版，加了那 4 行配置 |
| `agent_v1.py` | 视频里先跑的版本，没有那 4 行 |
| `utils.py` | 练习用的文件，有两个会导致崩溃的 bug，留给 Agent 修 |
| `.env.example` | `.env` 模板，DeepSeek 和 Claude 两种写法 |

## 运行

```bash
cp .env.example .env      # Windows：copy .env.example .env
# 打开 .env，填上你的 key
uv run agent.py
```

Agent 会直接改 `utils.py`。想恢复成有 bug 的原样再跑一次：

```bash
git checkout utils.py
```

## 跑 `agent_v1.py` 之前

`agent_v1.py` 没有限制工具，也会加载你电脑上的 Claude Code 配置（`~/.claude` 里的设置、插件、MCP 服务）。它可能会跑 Bash、派子 Agent、跑很久。想复现视频里的翻车可以跑，但要盯着，不对劲就按 `Ctrl+C`。

Agent 每次走的路线都不一样，你那边不一定会翻车。视频里录的两次都开着 `CLAUDE_CODE_EFFORT_LEVEL=max`：没加 4 行那次照样调了 Bash、Write、Grep，加了 4 行那次只用了 Glob、Read、Edit。

## 那 4 行

```python
tools=["Read", "Edit", "Glob"],  # 只给它这三个工具，清单外的工具对它来说不存在
setting_sources=[],              # 不加载电脑上的 user / project / local 设置
strict_mcp_config=True,          # 只用代码里给的 MCP 服务（这里一个也没给）
max_turns=20,                    # 保险丝：最多 20 轮
```

原来就有的 `allowed_tools` 只表示「这几个工具不用问我」，并不是「只能用这几个」。

## 参考

- Agent SDK 快速入门：https://code.claude.com/docs/en/agent-sdk/quickstart
- Python SDK 参考：https://code.claude.com/docs/en/agent-sdk/python
- DeepSeek 接入 Claude Code：https://api-docs.deepseek.com/zh-cn/quick_start/agent_integrations/claude_code

录制时的版本：claude-agent-sdk 0.2.181（内置 Claude Code 2.1.323），Python 3.12。
