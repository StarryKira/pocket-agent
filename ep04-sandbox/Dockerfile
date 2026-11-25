FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:0.11 /uv /usr/local/bin/uv

# 换成普通用户：Claude Code 不肯以 root 身份跳过权限确认
RUN useradd --create-home claude
USER claude
WORKDIR /home/claude/my-agent

# 把她的房间复制进容器（.env 和 .venv 不复制，见 .dockerignore）
COPY --chown=claude . .
RUN uv sync --frozen

ENV IN_DOCKER=1
ENTRYPOINT ["uv", "run", "agent.py"]
