import asyncio
from dotenv import load_dotenv
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ResultMessage

load_dotenv()  # 把 .env 里的配置读进环境变量


async def main():
    options = ClaudeAgentOptions(
        tools=["Read", "Edit", "Glob"],          # 只给它这三个工具
        allowed_tools=["Read", "Edit", "Glob"],  # 这几个工具不用问我，直接用
        permission_mode="acceptEdits",           # 改文件也不用问我
        setting_sources=[],                      # 不继承电脑上 ~/.claude 的配置
        strict_mcp_config=True,                  # 不继承任何 MCP 服务
        max_turns=20,                            # 保险丝：最多 20 轮
    )
    async for message in query(prompt="检查 utils.py 里会导致崩溃的 bug，修好它", options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if hasattr(block, "text"):
                    print(block.text)
                elif hasattr(block, "name"):
                    print(f"[工具] {block.name}")
        elif isinstance(message, ResultMessage):
            print(f"完成：{message.subtype}，共 {message.num_turns} 轮")


asyncio.run(main())
