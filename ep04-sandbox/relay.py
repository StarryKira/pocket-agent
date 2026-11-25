"""门卫：箱子里的 Claude娘 只连得到这里。
只放行发给大脑的请求（POST /v1/messages），替她带上真 key；别的一律拦下。
信也要拆开看：让大脑的服务器替她上网的请求，同样拦下。
只用 Python 标准库，compose.yaml 里直接拿官方 python 镜像跑。
"""
import http.client
import http.server
import json
import os
import urllib.parse

REAL = urllib.parse.urlsplit(os.environ.get("ANTHROPIC_BASE_URL", "https://api.anthropic.com"))  # 真正的大脑地址
TOKEN = os.environ.get("ANTHROPIC_AUTH_TOKEN")                   # 真 key 只在门卫这里
API_KEY = os.environ.get("ANTHROPIC_API_KEY")                    # （用 Claude 官方 API 时是这个）
ALLOW = {"/v1/messages", "/v1/messages/count_tokens"}
KEEP = {"content-type", "anthropic-version", "anthropic-beta"}          # 信封上只抄这几行，其余的不带出门


def fetches_web(x):
    # 服务端工具（web_search、deepseek_read_url…）带 "type"，Claude Code 自己的工具不带；
    # 图片、文档也能写成网址，让大脑的服务器去下载
    if isinstance(x, dict):
        src = x.get("source")
        if isinstance(src, dict) and src.get("type") == "url":
            return True
        return any(fetches_web(v) for v in x.values())
    if isinstance(x, list):
        return any(fetches_web(v) for v in x)
    return False


class Door(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        url = urllib.parse.urlsplit(self.path)
        if url.netloc or url.path not in ALLOW:
            return self.refuse()
        body = self.rfile.read(int(self.headers["Content-Length"]))
        try:
            req = json.loads(body)
            web = any("type" in t for t in req.get("tools", [])) or "mcp_servers" in req or fetches_web(req)
        except (ValueError, TypeError, AttributeError):
            return self.refuse("看不懂的信")
        if web:
            return self.refuse("想让大脑替她上网")
        headers = {k: v for k, v in self.headers.items() if k.lower() in KEEP}
        if TOKEN:
            headers["Authorization"] = f"Bearer {TOKEN}"
        else:
            headers["x-api-key"] = API_KEY
        conn = http.client.HTTPSConnection if REAL.scheme == "https" else http.client.HTTPConnection
        up = conn(REAL.hostname, REAL.port, timeout=600)
        up.request("POST", REAL.path.rstrip("/") + url.path + ("?" + url.query if url.query else ""), body, headers)
        r = up.getresponse()
        self.send_response(r.status)
        self.send_header("Content-Type", r.getheader("Content-Type", "application/json"))
        self.end_headers()
        while chunk := r.read1(65536):          # 大脑是一个字一个字流回来的，原样往回送
            self.wfile.write(chunk)
            self.wfile.flush()
        print(f"放行 {url.path} → {r.status}", flush=True)

    def do_GET(self):
        self.refuse()

    def refuse(self, why=""):
        print(f"拦下 {self.command} {self.path} {why}", flush=True)
        self.send_response(403)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write("门卫：这扇门只通往大脑\n".encode())

    def log_message(self, *args):
        pass


http.server.ThreadingHTTPServer(("0.0.0.0", 8080), Door).serve_forever()
