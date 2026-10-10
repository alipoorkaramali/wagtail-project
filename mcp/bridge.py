"""
MCP Universal Bridge for wagtail-mcp (v3 - absolute URL + path variants)
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

# ---------- Config ----------
TARGET_URL = os.environ.get("MCP_TARGET_URL", "http://127.0.0.1:8000/mcp/")
TOKEN = os.environ.get("MCP_TOKEN", "").strip()
HOST = os.environ.get("MCP_HOST", "127.0.0.1")
PORT = int(os.environ.get("MCP_PORT", "8002"))
PUBLIC_URL = os.environ.get("MCP_PUBLIC_URL", "https://tall-mandate-safely.ngrok-free.dev")
SESSION_TIMEOUT = int(os.environ.get("MCP_SESSION_TIMEOUT", "600"))
CLEANUP_INTERVAL = 60

HOP_BY_HOP = {
    "host", "connection", "content-length", "transfer-encoding",
    "keep-alive", "proxy-authenticate", "proxy-authorization",
    "te", "trailer", "upgrade", "authorization",
}

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
    while True:
        await asyncio.sleep(CLEANUP_INTERVAL)
        try:
            stale = [sid for sid, s in sessions.items() if s.is_stale()]
            for sid in stale:
                print(f"[bridge] Cleaning stale: {sid[:8]}")
                try:
                    await sessions[sid].queue.put(None)
                except Exception:
                    pass
                sessions.pop(sid, None)
        except Exception as e:
            print(f"[bridge] Cleanup error: {e}")

async def lifespan(app: FastAPI):
    global http_client
    if not TOKEN:
        raise SystemExit("MCP_TOKEN not set")
    http_client = httpx.AsyncClient(timeout=httpx.Timeout(120.0, connect=10.0))
    asyncio.create_task(cleanup_loop())
    print("=" * 60)
    print(f"[bridge] Target:    {TARGET_URL}")
    print(f"[bridge] Public:    {PUBLIC_URL}")
    print(f"[bridge] Token:     {TOKEN[:20]}... (len={len(TOKEN)})")
    print(f"[bridge] Listen:    http://{HOST}:{PORT}")
    print("=" * 60)
    yield
    if http_client:
        await http_client.aclose()

app = FastAPI(title="MCP Universal Bridge", lifespan=lifespan)

@app.get("/health")
async def health():
    return {"status": "ok", "sessions": len(sessions)}

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

    print(f"[bridge] PASSTHROUGH {request.method} {request.url.path}")

    try:
        req = http_client.build_request(
            method=request.method, url=target,
            headers=forward_headers,
            content=body if body else None,
        )
        resp = await http_client.send(req, stream=True)
    except Exception as e:
        print(f"[bridge] PASSTHROUGH ERROR: {e}")
        return JSONResponse({"error": str(e)}, status_code=502)

    resp_headers = {}
    for key, value in resp.headers.items():
        if key.lower() not in HOP_BY_HOP:
            resp_headers[key] = value

    print(f"[bridge] PASSTHROUGH <- {resp.status_code}")

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
#  SSE endpoint - sends ABSOLUTE URL
# ============================================================
@app.get("/sse")
async def sse_endpoint(request: Request):
    session_id = str(uuid.uuid4())
    session = Session(session_id)
    sessions[session_id] = session
    print(f"[bridge] >>> SSE NEW {session_id[:8]}")

    # Build absolute endpoint URL using public URL
    endpoint_url = f"{PUBLIC_URL}/messages/?session_id={session_id}"

    async def event_stream():
        # Send ABSOLUTE URL - some clients require this
        yield f"event: endpoint\ndata: {endpoint_url}\n\n"
        print(f"[bridge] >>> Sent endpoint: {endpoint_url}")
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
            print(f"[bridge] <<< SSE CLOSED {session_id[:8]}")

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"},
    )

# ============================================================
#  Message endpoints - register BOTH /messages and /messages/
# ============================================================
async def _handle_message(request: Request):
    session_id = request.query_params.get("session_id")
    print(f"[bridge] >>> MESSAGE received! session={session_id}")
    
    if not session_id:
        return JSONResponse({"error": "missing session_id"}, status_code=400)

    session = sessions.get(session_id)
    if not session:
        print(f"[bridge] !!! session not found: {session_id}")
        return JSONResponse({"error": "invalid session"}, status_code=404)

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
#  Catch-all for debugging - log unknown requests
# ============================================================
@app.api_route("/{path:path}", methods=["GET", "POST", "DELETE", "PUT", "PATCH"])
async def catch_all(request: Request, path: str):
    print(f"[bridge] !!! UNKNOWN {request.method} /{path}")
    return JSONResponse({"error": f"unknown path: /{path}"}, status_code=404)

if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT, log_level="info", access_log=True)
