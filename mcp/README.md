# MCP Bridge — Grok connector setup

## Connector settings (copy these)

| Field | Value |
|-------|--------|
| **Name** | `wagtail-sandbox` |
| **URL** | `https://wagtail-sandbox.codered.cloud/sse` |

No API key in the Grok UI — the server injects `MCP_TOKEN`.

### Steps in Grok

1. Open [https://grok.com/connectors](https://grok.com/connectors)
2. **Add connector** → **Custom** (or MCP / URL connector)
3. **Name:** `wagtail-sandbox`
4. **URL / Server URL:** `https://wagtail-sandbox.codered.cloud/sse`
5. Save and enable the connector for the chat

If it was already added and tools time out: **Disconnect → Connect** again (or delete and re-add).

---

## Endpoints on this site

| URL | Purpose |
|-----|--------|
| `https://wagtail-sandbox.codered.cloud/sse` | **Grok connector URL** (SSE) |
| `https://wagtail-sandbox.codered.cloud/messages/` | SSE message intake |
| `https://wagtail-sandbox.codered.cloud/mcp-bridge/health` | Health check |
| `https://wagtail-sandbox.codered.cloud/mcp/` | Native wagtail-mcp (needs `Authorization: Bearer wagtail_...`) |

### Server env (CodeRed)

- `MCP_TOKEN` = Wagtail API token starting with `wagtail_`
- `MCP_PUBLIC_URL` = `https://wagtail-sandbox.codered.cloud` (optional; auto from host)

### Delivery

1. **SSE queue** — standard path for Grok
2. **HTTP body fallback** — `/messages/` also returns `{ "status": "ok", "result": ... }` so a result is not lost if the stream is blocked

### Security

Anyone who knows the `/sse` URL can use tools with that token’s permissions. Prefer a limited token on production.
