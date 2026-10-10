"""
MCP Universal Bridge for wagtail-mcp  (cloud-ready)

Converts wagtail-mcp's StreamableHTTP endpoint to SSE for clients
(like Grok) that only speak the older SSE transport.

Also passes StreamableHTTP requests straight through, so any client
that supports either transport can use the same bridge.

Environment variables
---------------------
MCP_TOKEN         (required) - Wagtail API token, must start with "wagtail_"
MCP_TARGET_URL    (optional) - Where wagtail-mcp lives. Default: http://127.0.0.1:8000/mcp/
MCP_PUBLIC_URL    (optional) - Public URL of this bridge. Used in the SSE endpoint message.
MCP_PORT / PORT   (optional) - Port to listen on. Default: 8002
MCP_HOST          (optional) - Host to bind. Default: 0.0.0.0
MCP_SESSION_TIMEOUT (optional) - Session idle timeout in seconds. Default: 600
"""
import asyncio
import os
import time
import uuid
from typing import Dict

import httpx
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse

# ---------- Config from environment ----------
TARGET_URL = os.environ.get("MCP_TARGET_URL", "http://127.0.0.1:8000/mcp/").rstrip("/") + "/"
TOKEN = (os.environ.get("MCP_TOKEN", "") or "").strip()
PUBLIC_URL = os.environ.get("MCP_PUBLIC_URL", "").rstrip("/")
HOST = os.environ.get("MCP_HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", os.environ.get("MCP_PORT", "8002")))
SESSION_TIMEOUT = int(os.environ.get("MCP_SESSION_TIMEOUT", "600"))
CLEANUP_INTERVAL = 60

# Headers we don't forward to the target
HOP_BY_HOP = {
    "host", "connection", "content-length", "transfer-encoding",
    "keep-alive", "proxy-authenticate", "proxy-authorization",
    "te", "trailer", "upgrade", "authorization",
}

# ============================================================
#  Sessions for SSE transport
# ============================================================
class Session:
    __slots__ = ("id", "queue", "created", "last_activity")

    def __init__(self, session_id: str):
        self.id = session_id
        self.queue: asyncio.Queue = asyncio.Queue()
        self.created = time.time()
        self.last_activity = time.time()

    def touch(self):
        self.last_activity = time.time()

    def is_stale(self) -> bool:
        return (time.time() - self.last_activity) > SESSION_TIMEOUT

sessions: Dict[str, Session] = {}
http_client: httpx.AsyncClient = None

async def cleanup_loop():
    """Periodically close stale sessions to prevent memory leaks."""
    while True:
        await asyncio.sleep(CLEANUP_INTERVAL)
        try:
            stale = [sid for sid, s in sessions.items() if s.is_stale()]
            for sid in stale:
                print(f"[bridge] Cleaning stale session: {sid[:8]}")
                try:
                    await sessions[sid].queue.put(None)
                except Exception:
                    pass
                sessions.pop(sid, None)
            if stale:
                print(f"[bridge] Cleaned {len(stale)} stale sessions. Active: {len(sessions)}")
        except Exception as e:
            print(f"[bridge] Cleanup error: {e}")

# ============================================================
#  FastAPI app with lifespan
# ============================================================
async def lifespan(app: FastAPI):
    global http_client
    if not TOKEN:
        raise SystemExit("MCP_TOKEN environment variable is not set")
    if not TOKEN.startswith("wagtail_"):
        print(f"[bridge] WARNING: MCP_TOKEN does not start with 'wagtail_' (got: {TOKEN[:15]}...)")
    http_client = httpx.AsyncClient(timeout=httpx.Timeout(120.0, connect=10.0))
    asyncio.create_task(cleanup_loop())
    print("=" * 60)
    print(f"[bridge] Target:     {TARGET_URL}")
    print(f"[bridge] Public URL: {PUBLIC_URL or '(auto-detect per request)'}")
    print(f"[bridge] Token:      {TOKEN[:20]}... (len={len(TOKEN)})")
    print(f"[bridge] Listening:  http://{HOST}:{PORT}")
    print(f"[bridge] Endpoints:")
    print(f"[bridge]   StreamableHTTP: POST /mcp | GET /mcp")
    print(f"[bridge]   Legacy SSE:     GET /sse | POST /messages/")
    print("=" * 60)
    yield
    if http_client:
        await http_client.aclose()

app = FastAPI(title="MCP Universal Bridge", lifespan=lifespan)

# ============================================================
#  Health check
# ============================================================
@app.get("/")
@app.get("/health")
async def health():
    return {
        "status": "ok",
        "sessions": len(sessions),
        "target": TARGET_URL,
        "public_url": PUBLIC_URL or None,
    }

# ============================================================
#  StreamableHTTP passthrough
# ============================================================
async def _passthrough(request: Request):
    forward_headers = {}
    for key, value in request.headers.items():
        if key.lower() not in HOP_BY_HOP:
            forward_headers[key] = value
    forward_headers["Authorization"] = f"Bearer {TOKEN}"

    body = await request.body()
    target = TARGET_URL
    if request.url.query:
        target = f"{target}?{request.url.query}"

    print(f"[bridge] PASSTHROUGH {request.method} {request.url.path} -> {target}")

    try:
        req = http_client.build_request(
            method=request.method,
            url=target,
            headers=forward_headers,
            content=body if body else None,
        )
        resp = await http_client.send(req, stream=True)
    except Exception as e:
        print(f"[bridge] PASSTHROUGH ERROR: {e}")
        return JSONResponse({"error": f"upstream error: {e}"}, status_code=502)

    resp_headers = {}
    for key, value in resp.headers.items():
        if key.lower() not in HOP_BY_HOP:
            resp_headers[key] = value

    print(f"[bridge] PASSTHROUGH <- {resp.status_code} ({resp.headers.get('content-type', '?')})")

    async def stream_body():
        try:
            async for chunk in resp.aiter_bytes():
                yield chunk
        finally:
            await resp.aclose()

    return StreamingResponse(stream_body(), status_code=resp.status_code, headers=resp_headers)

@app.api_route("/mcp", methods=["GET", "POST", "DELETE", "PUT", "PATCH"])
async def mcp_no_slash(request: Request):
    return await _passthrough(request)

@app.api_route("/mcp/", methods=["GET", "POST", "DELETE", "PUT", "PATCH"])
async def mcp_slash(request: Request):
    return await _passthrough(request)

# ============================================================
#  Legacy SSE transport
# ============================================================
def _public_base(request: Request) -> str:
    """Determine the public base URL for building the SSE endpoint message."""
    if PUBLIC_URL:
        return PUBLIC_URL
    # Fallback: use the incoming request's scheme + host
    scheme = request.headers.get("x-forwarded-proto", request.url.scheme)
    host = request.headers.get("x-forwarded-host", request.headers.get("host", ""))
    if host:
        return f"{scheme}://{host}"
    return ""

@app.get("/sse")
async def sse_endpoint(request: Request):
    session_id = str(uuid.uuid4())
    session = Session(session_id)
    sessions[session_id] = session
    print(f"[bridge] >>> SSE NEW {session_id[:8]} (total: {len(sessions)})")

    base = _public_base(request)
    endpoint_url = f"{base}/messages/?session_id={session_id}"
    print(f"[bridge] >>> endpoint: {endpoint_url}")

    async def event_stream():
        yield f"event: endpoint\ndata: {endpoint_url}\n\n"
        try:
            while True:
                try:
                    msg = await asyncio.wait_for(session.queue.get(), timeout=25.0)
                except asyncio.TimeoutError:
                    yield ": ping\n\n"
                    continue
                if msg is None:
                    break
                session.touch()
                yield f"event: message\ndata: {msg}\n\n"
        except asyncio.CancelledError:
            print(f"[bridge] SSE client left {session_id[:8]}")
        finally:
            sessions.pop(session_id, None)
            print(f"[bridge] <<< SSE CLOSED {session_id[:8]} (active: {len(sessions)})")

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )

async def _handle_message(request: Request):
    session_id = request.query_params.get("session_id")
    print(f"[bridge] >>> MESSAGE session={session_id}")

    if not session_id:
        return JSONResponse({"error": "missing session_id"}, status_code=400)

    session = sessions.get(session_id)
    if not session:
        print(f"[bridge] !!! unknown session: {session_id}")
        return JSONResponse({"error": "invalid or expired session"}, status_code=404)

    session.touch()

    try:
        body = await request.json()
    except Exception as e:
        return JSONResponse({"error": f"bad json: {e}"}, status_code=400)

    print(f"[bridge] >>> MESSAGE method={body.get('method', '?')}")

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }

    try:
        resp = await http_client.post(TARGET_URL, json=body, headers=headers)
    except Exception as e:
        err = '{"jsonrpc":"2.0","id":null,"error":{"code":-32603,"message":"bridge error"}}'
        await session.queue.put(err)
        print(f"[bridge] !!! upstream error: {e}")
        return JSONResponse({"status": "queued"}, status_code=202)

    print(f"[bridge] <<< upstream {resp.status_code}")

    ct = resp.headers.get("content-type", "")
    if ct.startswith("text/event-stream"):
        for line in resp.text.splitlines():
            if line.startswith("data:"):
                data = line[5:].strip()
                if data:
                    await session.queue.put(data)
    else:
        text = resp.text.strip()
        if text:
            await session.queue.put(text)

    return JSONResponse({"status": "queued"}, status_code=202)

@app.post("/messages/")
async def messages_slash(request: Request):
    return await _handle_message(request)

@app.post("/messages")
async def messages_no_slash(request: Request):
    return await _handle_message(request)

# ============================================================
#  Entrypoint
# ============================================================
if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT, log_level="info", access_log=True)
