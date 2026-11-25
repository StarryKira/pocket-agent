# 03｜给 Claude娘 一个终端，她没问我就删了 387 兆

视频：（发布后补链接）

给 Agent 加上 Bash（能跑终端命令），再用 `can_use_tool` 让没被提前放行的工具调用都先来问你：

- `agent.py`：最终版。权限模式 `default`，只有 Read、Glob 不用问，其余的（包括每一条不在只读名单上的 Bash 命令）都会打印出来等你按 y / n；按 n 之后可以再输入一句理由，Agent 会看到这句话。
- `agent_v1.py`：翻车版，沿用上一集的 `acceptEdits` + `allowed_tools=["Read", "Edit", "Glob"]`。**它会在不问你的情况下执行工作目录里的 `rm`、`mv`、`cp`、`sed`**，只在可以随便删的副本里跑。

## 运行

```bash
cp .env.example .env      # Windows：copy .env.example .env
# 打开 .env，填上你的 key
uv run agent.py "这个项目文件夹太占地方了，帮我清理一下"
```

不传任务时默认就是上面这句。项目里最大的是 `.venv`；你同意删的话它会被删掉，下次 `uv run` 会自动装回来。

输出大概是这样（每次跑的路线都不一样）：

```
[thinking] The user wants me to clean up the project folder ...
[工具] Bash du -sh .venv/* 2>/dev/null | sort -rh | head -15

🙋 她想用 Bash：rm -rf -- .venv && echo "已删除 .venv" && du -sh . && ls -la
   她的说明：Remove the reproducible virtualenv and show resulting size
   让她做吗？(y/n) n
   为什么不行？（她会看到这句话）这个别删。缓存可以删，其他文件先留着。
…
—— 完成
```

## 几个要点

- **检查顺序。** 每次工具调用，Claude Code 按 hooks → 禁止规则（`disallowed_tools`）→ 询问规则 → 权限模式 → 允许规则（`allowed_tools`）→ `can_use_tool` 的顺序检查，前面哪一步放行了，就不会走到你的函数。
- **`acceptEdits` 不只是「改文件不用问」。** 它还会自动放行工作目录里的 `mkdir`、`touch`、`rm`、`rmdir`、`mv`、`cp`、`sed`。
- **只读命令永远不问。** `ls`、`cat`、`du`、`grep`、`find`、只读的 `git` 等在任何模式下都直接执行，包括 `cat .env`。别让能跑 Bash 的 Agent 在放着真 key 的目录里随便翻。
- **启动时的 `CanUseToolShadowedWarning`。** `allowed_tools` 里写了整个工具名（比如 `"Read"`），SDK 会提醒这些工具不会经过 `can_use_tool`。它不会提醒 `acceptEdits` 放行的那些命令。
- **拒绝时的理由会原样交给 Agent。** 它会当成你说的话来理解；说得含糊，它可能会理解成别的东西（视频里「缓存可以删」被理解成整台电脑的 uv 缓存）。
- **`input()` 放进 `asyncio.to_thread`。** 回调是 async 的，直接调用 `input()` 会卡住事件循环。
- 新版 Python SDK 里 `can_use_tool` 直接用字符串 prompt 就行；官方文档里「流式 prompt + 空的 PreToolUse hook」是旧版本的写法。

## 参考

- Configure permissions：https://code.claude.com/docs/en/agent-sdk/permissions
- Handle approvals and user input：https://code.claude.com/docs/en/agent-sdk/user-input
- Permissions（只读命令、Bash 规则）：https://code.claude.com/docs/en/permissions

录制时的版本：claude-agent-sdk 0.2.184（内置 Claude Code 2.1.327），Python 3.12。
