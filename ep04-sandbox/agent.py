import asyncio
import os
import sys
from dotenv import load_dotenv
from claude_agent_sdk import (query, ClaudeAgentOptions, AssistantMessage, ResultMessage,
                              ThinkingBlock, TextBlock, ToolUseBlock,
                              PermissionResultAllow, PermissionResultDeny)

load_dotenv()  # 把 .env 里的配置读进环境变量


async def ask_me(tool, args, context):
    # 沙盒管不了、又没被提前放行的请求，会走到这里，等我回答
    if tool == "SandboxNetworkAccess":
        print(f"\n🙋 她想连网：{args['host']}")
    elif args.get("dangerouslyDisableSandbox"):
        print(f"\n🙋 她想到沙盒外面跑：{args['command']}")
    else:
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
        tools=["Read", "Edit", "Glob", "Bash"],
        allowed_tools=["Read", "Glob"],
        permission_mode="default",
        can_use_tool=ask_me,
        sandbox={
            "enabled": True,                     # 她跑的每条命令，都关进沙盒
            "autoAllowBashIfSandboxed": True,    # 沙盒里的命令不用问我（新版默认是 False）
            "filesystem": {"denyRead": ["~/.ssh", "~/.aws"]},  # 这些连看都不让看
        },
        setting_sources=[],                      # 不继承电脑上 ~/.claude 的配置
        strict_mcp_config=True,                  # 不继承任何 MCP 服务
        max_turns=30,                            # 保险丝
    )
    if os.getenv("IN_DOCKER") == "1":            # Dockerfile 里设的
        # 她整个人都在容器里了：什么都不问，也不用再套一层沙盒
        options.permission_mode = "bypassPermissions"
        options.can_use_tool = None
        options.sandbox = None

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
