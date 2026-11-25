# 04｜把 Claude娘 关进箱子，她借 DeepSeek 溜了出去

视频：（发布后补链接）

在上一集（Bash + `can_use_tool`）的基础上，先用 Agent SDK 自带的沙盒把她的终端命令关起来，再把她整个装进 Docker，箱子只留一扇门。

- `agent.py`：在 Mac / Linux 上直接跑时开 `sandbox`：她跑的每条 Bash 命令都在操作系统的沙盒里（macOS 是 Seatbelt），只能写项目文件夹和临时目录，上网要走白名单（默认为空）；`~/.ssh`、`~/.aws` 连读都不让读。沙盒挡住的事，她如果想到沙盒外面做、或者想连某个网站，会弹给你 y / n。在 Docker 里（`IN_DOCKER=1`）则什么都不问。
- `Dockerfile`：把这个文件夹装进一个 Python 镜像，用普通用户运行。
- `compose.yaml` + `relay.py`：箱子只接一个不通外面的内网；唯一能连的是门卫 `relay.py`。门卫只转发发给模型的请求（`POST /v1/messages`），替她换上真 key；她手里只有 `sk-xxxx`。

## 运行

```bash
cp .env.example .env      # Windows：copy .env.example .env
# 打开 .env，填上你的 key

# 1. 在本机跑，带沙盒（macOS / Linux / WSL2）
uv run agent.py "这个项目文件夹太占地方了，帮我清理一下"

# 2. 整个装进箱子（需要 Docker Desktop 或 OrbStack）
docker compose run --rm claude "这个项目文件夹太占地方了，帮我清理一下"
docker compose logs relay     # 看门卫放行、拦下了什么
docker compose down           # 用完把门卫也停掉
```

`docker compose run` 第一次会构建镜像（要联网下载依赖，一两分钟）。箱子里的 `.venv` 删了也没关系：`--rm` 让箱子用完就扔，下次从镜像重新开一个。

## 几个要点

- **`autoAllowBashIfSandboxed` 要自己写上。** Claude Code 2.1.324 起默认是 `false`：开了沙盒，命令照样一条条问你。SDK 代码里的注释还写着默认 `True`，以文档为准。
- **沙盒只套住 Bash。** 她的 Read / Edit 工具和 Claude Code 程序本身都在沙盒外面；默认几乎能读整台电脑，所以要 `denyRead`。想让她完全无人看管地跑，官方的说法是放进容器或虚拟机，并且用普通用户。
- **`SandboxNetworkAccess`。** 沙盒里的命令要连白名单外的网站时，`can_use_tool` 收到的工具名是它，参数是 `{"host": ...}`。
- **Docker 默认能上网，`--env-file` 会把 key 交给容器。** 所以 compose 里箱子只接 `internal: true` 的网络，key 只给门卫。
- **只放行 `/v1/messages` 还不够。** 模型服务商有「服务端工具」（网页搜索、读网页），在服务商的服务器上执行，请求本身就是发给模型的。DeepSeek 的 Anthropic 兼容接口支持 `web_search_20250305`、`web_search_20260209`、`deepseek_web_search`、`deepseek_read_url`，图片也能写成网址让服务器去下载。`relay.py` 会拆开请求体：带 `type` 的工具（Claude Code 自己的工具都不带）、`mcp_servers`、`"source": {"type": "url"}` 的内容一律拒绝；只转发三个请求头。
- **门卫不是万能的。** 她发给模型的每句话、读到的文件内容，照样会经过门卫送到服务商那里。官方文档：Within your proxy's allowlist, the agent can send data to any allowed domain.
- 用 Claude 官方 API 时：`.env` 里写 `ANTHROPIC_API_KEY`，并把 `compose.yaml` 里 `claude` 的 `ANTHROPIC_AUTH_TOKEN: sk-xxxx` 改成 `ANTHROPIC_API_KEY: sk-xxxx`（不然 `env_file` 会把真 key 交给箱子）。门卫会用 `.env` 里真的 `ANTHROPIC_API_KEY`，地址默认是 `https://api.anthropic.com`。

## 参考

- Configure the sandboxed Bash tool：https://code.claude.com/docs/en/sandboxing
- Settings reference（`sandbox.*`）：https://code.claude.com/docs/en/settings-reference
- Permission modes（`bypassPermissions`）：https://code.claude.com/docs/en/permission-modes
- Securely deploying AI agents（容器、代理模式）：https://code.claude.com/docs/en/agent-sdk/secure-deployment

录制时的版本：claude-agent-sdk 0.2.188（内置 Claude Code 2.1.331），Python 3.12，Docker 29.8（OrbStack）。
