# MCP Bridge

## Preferred setup (CodeRed — no extra account)

The **in-app** bridge lives in the Django app `mcp_bridge` and is served on the same site:

| URL | Purpose |
|-----|--------|
| `https://wagtail-sandbox.codered.cloud/sse` | Grok custom connector (SSE) |
| `https://wagtail-sandbox.codered.cloud/messages/` | SSE message intake |
| `https://wagtail-sandbox.codered.cloud/mcp-bridge/health` | Health check |
| `https://wagtail-sandbox.codered.cloud/mcp/` | Native wagtail-mcp (needs Bearer token) |

### Setup

1. In **CodeRed Cloud** dashboard → your site → **Environment variables**, add:

   - `MCP_TOKEN` = your Wagtail API token (`wagtail_...`)

2. Deploy the site (GitHub Actions → **Deploy to CodeRed Cloud** → Run workflow).

3. In Grok → [connectors](https://grok.com/connectors) → **Custom**:

   - **Name:** e.g. `Wagtail Sandbox`
   - **URL:** `https://wagtail-sandbox.codered.cloud/sse`

No ngrok, no Render, no laptop terminal.

### Security note

`/sse` does not ask Grok for a token; the server injects `MCP_TOKEN`.
Anyone who knows the URL can use MCP tools with that token's permissions.
Use a token with limited permissions on production sites.

---

## Standalone FastAPI bridge (optional)

The files in this folder (`bridge.py`) are an optional separate service
for local/ngrok or Render. Prefer the in-app Django bridge above.
