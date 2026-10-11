# MCP Universal Bridge

A small FastAPI service that makes `wagtail-mcp` usable from any
MCP client, regardless of which transport they support.

## Why does this exist?

`wagtail-mcp` speaks **StreamableHTTP**. Some clients (like Grok's
current web connector) only support the older **SSE** transport.
This bridge accepts **both** and forwards everything to `wagtail-mcp`.

```
Grok ──SSE──▶ Bridge ──StreamableHTTP──▶ wagtail-mcp (Django)
│
└── StreamableHTTP ──▶ wagtail-mcp (passthrough)
```

## Endpoints

| Path | Method | Purpose |
|------|--------|---------|
| `/` | GET | Health check + stats |
| `/health` | GET | Same as `/` |
| `/mcp` | POST/GET/DELETE | StreamableHTTP passthrough |
| `/mcp/` | POST/GET/DELETE | Same, with trailing slash |
| `/sse` | GET | SSE session (legacy transport) |
| `/messages/` | POST | SSE message intake |
| `/messages` | POST | Same, without trailing slash |

## Environment variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `MCP_TOKEN` | ✅ | — | Wagtail API token (starts with `wagtail_`) |
| `MCP_TARGET_URL` | | `http://127.0.0.1:8000/mcp/` | Where wagtail-mcp lives |
| `MCP_PUBLIC_URL` | | auto-detect | Public URL of this bridge |
| `PORT` / `MCP_PORT` | | `8002` | Port to listen on |
| `MCP_HOST` | | `0.0.0.0` | Host to bind |
| `MCP_SESSION_TIMEOUT` | | `600` | Idle session timeout (seconds) |

## Local development

```bash
# 1. Activate the venv that has fastapi + uvicorn + httpx
# 2. Set the environment
export MCP_TOKEN=wagtail_your_token_here
export MCP_TARGET_URL=http://127.0.0.1:8000/mcp/
export MCP_PUBLIC_URL=https://your-ngrok-url.ngrok-free.dev

# 3. Run
python bridge.py
```

## Cloud deployment (Render)

1. Create a new **Web Service** on Render
2. Point it at this repository, **Root Directory = `mcp`**
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn bridge:app --host 0.0.0.0 --port $PORT`
5. Add environment variables:

- `MCP_TOKEN` = your Wagtail token
- `MCP_TARGET_URL` = `https://your-django-app.onrender.com/mcp/`
- `MCP_PUBLIC_URL` = `https://your-bridge.onrender.com`
6. Deploy

The public URL for Grok is: `https://your-bridge.onrender.com/sse`

## Verifying it works

```bash
# Local test
curl -N http://127.0.0.1:8002/sse

# Should print:
# event: endpoint
# data: /messages/?session_id=...
```
