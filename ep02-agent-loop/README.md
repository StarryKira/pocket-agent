# 02｜修 9 行代码，她读了 10 万 token

视频：（发布后补链接）

在上一集 `agent.py` 的基础上改了几行，让 Agent 每一轮都把自己在干什么打出来：

- 每一轮（模型回复一次）开头打印：第几轮、这一轮的上下文有多少 token
- 打印 thinking（模型回答之前的推理过程，SDK 里叫 `ThinkingBlock`；上一集的代码把它漏掉了）
- 打印每次工具调用的参数
- 最后打印一共读了多少 token、其中多少命中缓存

## 运行

```bash
cp .env.example .env      # Windows：copy .env.example .env
# 打开 .env，填上你的 key
uv run agent.py
```

Agent 会直接改 `utils.py`。想恢复成有 bug 的原样再跑一次：`git checkout utils.py`。

输出大概是这样（每次跑的路线都不一样）：

```
—— 第 1 轮 · 上下文 1399 tokens
[thinking] Let me start by finding and reading utils.py in the working directory.
[工具] Glob {'pattern': '**/utils.py', 'path': '…/my-agent'}

—— 第 2 轮 · 上下文 1645 tokens
[thinking] The project's utils.py is at …/my-agent/utils.py. Let me read it.
[工具] Read {'file_path': '…/my-agent/utils.py'}
…
完成：9 轮，一共读了 61627 tokens，其中 50944 命中缓存
```

## 几个要点

- **一轮 = 模型回复一次。** 一次回复可能拆成好几条 `AssistantMessage`（thinking 一条、每个工具调用一条），它们共用同一个 `message_id`，所以按 `message_id` 分轮。`ResultMessage.num_turns` 的数法不一样，在我们的实验里它等于「工具调用次数 + 1」。
- **每一轮读的是整段上下文。** 模型接口不记得上一轮，SDK 每一轮都把系统提示词、工具定义、任务和前面所有的回复、工具结果从头再发一遍。`message.usage` 是这一次请求的用量。
- **缓存。** 跟上一轮开头一模一样的部分会命中缓存（`cache_read_input_tokens`），价格便宜得多。用 DeepSeek 时没有 `cache_creation_input_tokens`；用 Claude 时三项加起来才是这一轮的上下文。
- **少绕路。** 在任务里补一句背景（比如「项目里没有测试，也不用看别的文件」），轮数和 token 通常都会少很多。

用 Claude 模型时，thinking 可能是摘要或者不返回；DeepSeek 返回完整原文。

## 参考

- How the agent loop works：https://code.claude.com/docs/en/agent-sdk/agent-loop
- Python SDK 参考：https://code.claude.com/docs/en/agent-sdk/python
- DeepSeek Token 用量计算：https://api-docs.deepseek.com/zh-cn/quick_start/token_usage

录制时的版本：claude-agent-sdk 0.2.182（内置 Claude Code 2.1.325），Python 3.12。
