import asyncio
import sys
from dotenv import load_dotenv
from claude_agent_sdk import (query, ClaudeAgentOptions, AssistantMessage, ResultMessage,
                              ThinkingBlock, TextBlock, ToolUseBlock,
                              PermissionResultAllow, PermissionResultDeny)

load_dotenv()  # 把 .env 里的配置读进环境变量


async def ask_me(tool, args, context):
    # 前面的规则都没放行的工具调用，会走到这里，等我回答
    print(f"\n🙋 她想用 {tool}：{args.get('command') or args}")
    if args.get("description"):
        print(f"   她的说明：{args['description']}")
    answer = await asyncio.to_thread(input, "   让她做吗？(y/n) ")
    if answer.strip().lower() == "y":
        return PermissionResultAllow(updated_input=args)
    reason = await asyncio.to_thread(input, "   为什么不行？（她会看到这句话）")
    return PermissionResultDeny(message=reason or "不行")


async def main():
    task = " ".join(sys.argv[1:]) or "这个项目文件夹太占地方了，帮我清理一下"
    options = ClaudeAgentOptions(
        tools=["Read", "Edit", "Glob", "Bash"],  # 多了 Bash：能跑终端命令
        allowed_tools=["Read", "Glob"],          # 只有读文件、找文件不用问我
        permission_mode="default",               # 不再自动放行改文件和 rm
        can_use_tool=ask_me,                     # 其余的都来问我
        setting_sources=[],                      # 不继承电脑上 ~/.claude 的配置
        strict_mcp_config=True,                  # 不继承任何 MCP 服务
        max_turns=30,                            # 保险丝
    )
    async for message in query(prompt=task, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, ThinkingBlock):
                    if block.thinking:
                        print(f"[thinking] {block.thinking}")
                elif isinstance(block, TextBlock):
                    print(block.text)
                elif isinstance(block, ToolUseBlock):
                    print(f"[工具] {block.name} {block.input.get('command') or block.input}")
        elif isinstance(message, ResultMessage):
            print("\n—— 完成")


asyncio.run(main())
