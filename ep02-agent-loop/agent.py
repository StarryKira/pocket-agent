import asyncio
from dotenv import load_dotenv
from claude_agent_sdk import (query, ClaudeAgentOptions, AssistantMessage, ResultMessage,
                              ThinkingBlock, TextBlock, ToolUseBlock)

load_dotenv()  # 把 .env 里的配置读进环境变量


def context_tokens(usage):
    # 这一次请求，模型一共读了多少 token（没命中缓存的 + 写进缓存的 + 命中缓存的）
    return (usage.get("input_tokens", 0) + usage.get("cache_creation_input_tokens", 0)
            + usage.get("cache_read_input_tokens", 0))


async def main():
    options = ClaudeAgentOptions(
        tools=["Read", "Edit", "Glob"],          # 只给它这三个工具
        allowed_tools=["Read", "Edit", "Glob"],  # 这几个工具不用问我，直接用
        permission_mode="acceptEdits",           # 改文件也不用问我
        setting_sources=[],                      # 不继承电脑上 ~/.claude 的配置
        strict_mcp_config=True,                  # 不继承任何 MCP 服务
        max_turns=20,                            # 保险丝
    )
    rounds = []  # 每一轮（模型回复一次）的 message_id
    async for message in query(prompt="检查 utils.py 里会导致崩溃的 bug，修好它", options=options):
        if isinstance(message, AssistantMessage):
            if message.message_id not in rounds:  # 同一次回复拆成的几条消息共用一个 id
                rounds.append(message.message_id)
                print(f"\n—— 第 {len(rounds)} 轮 · 上下文 {context_tokens(message.usage)} tokens")
            for block in message.content:
                if isinstance(block, ThinkingBlock):
                    if block.thinking:
                        print(f"[thinking] {block.thinking}")
                elif isinstance(block, TextBlock):
                    print(block.text)
                elif isinstance(block, ToolUseBlock):
                    print(f"[工具] {block.name} {block.input}")
        elif isinstance(message, ResultMessage):
            u = message.usage
            print(f"\n完成：{len(rounds)} 轮，一共读了 {context_tokens(u)} tokens，"
                  f"其中 {u.get('cache_read_input_tokens', 0)} 命中缓存")


asyncio.run(main())
