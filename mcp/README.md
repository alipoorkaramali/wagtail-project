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
set MCP_TOKEN=wagtail_your_token_here
set MCP_TARGET_URL=http://127.0.0.1:8000/mcp/
set MCP_PUBLIC_URL=https://your-ngrok-url.ngrok-free.dev

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

```
# Local test
curl -N http://127.0.0.1:8002/sse

# Should print:
# event: endpoint
# data: /messages/?session_id=...
```

</BDS:create_file>

<BDS:create_file fileName="render.yaml">

```yaml
# Render Blueprint — deploys both services at once
# Docs: https://render.com/docs/blueprint-spec

services:
  # ---------- Service 1: Django + Wagtail + wagtail-mcp ----------
  - type: web
    name: wagtail-mcp-app
    runtime: python
    plan: free
    buildCommand: |
      pip install -r requirements.txt
      python manage.py collectstatic --noinput
      python manage.py migrate --noinput
    startCommand: gunicorn mysite.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120
    envVars:
      - key: PYTHON_VERSION
        value: 3.12.7
      - key: DJANGO_SETTINGS_MODULE
        value: mysite.settings.production
      - key: SECRET_KEY
        generateValue: true
      - key: DEBUG
        value: "False"
      - key: ALLOWED_HOSTS
        value: ".onrender.com"
      - key: DATABASE_URL
        fromDatabase:
          name: wagtail-mcp-db
          property: connectionString

  # ---------- Service 2: MCP Bridge ----------
  - type: web
    name: wagtail-mcp-bridge
    runtime: python
    plan: free
    rootDir: mcp
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn bridge:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.12.7
      - key: MCP_TOKEN
        sync: false               # set manually in Render UI
      - key: MCP_TARGET_URL
        value: "https://wagtail-mcp-app.onrender.com/mcp/"
      - key: MCP_PUBLIC_URL
        value: "https://wagtail-mcp-bridge.onrender.com"

databases:
  - name: wagtail-mcp-db
    plan: free
    databaseName: wagtail
    user: wagtail

