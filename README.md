# 手搓 AI 助理

用 [Claude Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview)（Python）从零搭一个私人 AI 助理，一集加一个能力。这里放视频的配套代码。

| 集 | 标题 | 代码 |
|---|---|---|
| 01 | 20 行代码的 Agent，为什么开了 15 个分身？ | [ep01-first-agent](ep01-first-agent/) |
| 02 | 拆开 agent loop（制作中） | — |

## 准备

- 终端：Mac 用自带的「终端」，Windows 用 PowerShell
- [uv](https://docs.astral.sh/uv/getting-started/installation/)：装 Python 和管理依赖都靠它
- 一把钥匙：DeepSeek API key（视频里用的），或者 Claude API key

不用单独安装 Claude Code，`claude-agent-sdk` 这个包已经带了。

## 跑起来

```bash
git clone https://github.com/StarryKira/pocket-agent.git
cd pocket-agent/ep01-first-agent
cp .env.example .env      # Windows：copy .env.example .env
# 打开 .env，填上你的 key
uv run agent.py
```

每一集的文件夹都是一个独立的 uv 项目，`uv run` 第一次会自动装好 Python 和依赖。

## 版本

Agent SDK 还没到 1.0，几乎每天都在发版。每个文件夹里的 `uv.lock` 锁定了录视频时用的版本，直接 `uv run` 就和视频里一致。想试最新版：

```bash
uv lock --upgrade
```

新版本的行为可能和视频里不一样。

## 钥匙安全

- key 只写在 `.env` 里，`.env` 已经写进 `.gitignore`，不会被提交。
- 不要把 key 写进代码，也不要截图、录屏时露出来。
- Claude 订阅（Pro / Max）登录只能自己用。不能把 Claude 账号登录做进给别人用的应用，也不能用订阅额度替别人跑请求，详见官方的[法律和合规](https://code.claude.com/docs/zh-CN/legal-and-compliance)页。

## 许可证

[MIT](LICENSE)：代码可以随便拿去用、改、商用，保留版权声明就行。
