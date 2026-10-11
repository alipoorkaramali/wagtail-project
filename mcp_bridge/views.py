"""
In-process MCP bridge for Grok and other clients that only send a URL
(no Bearer token in the connector UI).

Flow:
  Grok ──GET /sse──▶ this app ──(+ MCP_TOKEN)──▶ /mcp/ (wagtail-mcp)

Environment / settings:
  MCP_TOKEN       required — Wagtail API token (wagtail_...)
  MCP_TARGET_URL  optional — default https://{VIRTUAL_HOST}/mcp/ or /mcp/
  MCP_PUBLIC_URL  optional — default https://{VIRTUAL_HOST}
"""
from __future__ import annotations

import json
import logging
import queue
import uuid
from queue import Queue
from typing import Dict
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.conf import settings
from django.http import HttpRequest, HttpResponse, JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

logger = logging.getLogger(__name__)

# In-memory SSE sessions (fine for single-worker CodeRed plans).
_sessions: Dict[str, Queue] = {}
_SESSION_TTL = 600
_session_touch: Dict[str, float] = {}


def _token() -> str:
    return (getattr(settings, "MCP_TOKEN", None) or "").strip()


def _public_base(request: HttpRequest) -> str:
    configured = (getattr(settings, "MCP_PUBLIC_URL", None) or "").rstrip("/")
    if configured:
        return configured
    virtual = (getattr(settings, "VIRTUAL_HOST", None) or "").strip()
    if virtual:
        return f"https://{virtual}"
    scheme = request.headers.get("X-Forwarded-Proto") or request.scheme
    host = request.headers.get("X-Forwarded-Host") or request.get_host()
    return f"{scheme}://{host}"


def _target_url() -> str:
    configured = (getattr(settings, "MCP_TARGET_URL", None) or "").strip()
    if configured:
        return configured.rstrip("/") + "/"
    virtual = (getattr(settings, "VIRTUAL_HOST", None) or "").strip()
    if virtual:
        return f"https://{virtual}/mcp/"
    return "http://127.0.0.1:8000/mcp/"


def _cleanup_stale() -> None:
    now = time.time()
    stale = [sid for sid, ts in _session_touch.items() if now - ts > _SESSION_TTL]
    for sid in stale:
        _sessions.pop(sid, None)
        _session_touch.pop(sid, None)


def _call_mcp(body: dict) -> str:
    """POST JSON-RPC to wagtail-mcp with Bearer token; return response text."""
    token = _token()
    if not token:
        return json.dumps(
            {
                "jsonrpc": "2.0",
                "id": body.get("id"),
                "error": {
                    "code": -32000,
                    "message": "MCP_TOKEN is not configured on the server",
                },
            }
        )

    data = json.dumps(body).encode("utf-8")
    req = Request(
        _target_url(),
        data=data,
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "User-Agent": "mcp-bridge-django/1.0",
        },
    )
    try:
        with urlopen(req, timeout=120) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            content_type = resp.headers.get("Content-Type", "")
    except HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        content_type = e.headers.get("Content-Type", "") if e.headers else ""
        logger.warning("MCP upstream HTTP %s: %s", e.code, raw[:300])
    except URLError as e:
        logger.exception("MCP upstream connection error")
        return json.dumps(
            {
                "jsonrpc": "2.0",
                "id": body.get("id"),
                "error": {"code": -32603, "message": f"upstream error: {e}"},
            }
        )

    if content_type.startswith("text/event-stream"):
        chunks = []
        for line in raw.splitlines():
            if line.startswith("data:"):
                payload = line[5:].strip()
                if payload:
                    chunks.append(payload)
        return chunks[-1] if chunks else raw

    return raw.strip()


@csrf_exempt
@require_GET
def sse(request: HttpRequest):
    """Legacy MCP SSE transport — Grok connects here with only a URL."""
    _cleanup_stale()
    token = _token()
    if not token:
        return JsonResponse(
            {"error": "MCP_TOKEN is not set. Add it in CodeRed environment variables."},
            status=503,
        )

    session_id = str(uuid.uuid4())
    queue: Queue = Queue()
    _sessions[session_id] = queue
    _session_touch[session_id] = time.time()

    base = _public_base(request)
    endpoint_url = f"{base}/messages/?session_id={session_id}"
    logger.info("SSE session %s endpoint=%s", session_id[:8], endpoint_url)

    def event_stream():
        yield f"event: endpoint\ndata: {endpoint_url}\n\n"
        try:
            while True:
                try:
                    msg = queue.get(timeout=25)
                except Exception:
                    # keepalive so proxies don't close the stream
                    yield ": ping\n\n"
                    continue
                if msg is None:
                    break
                _session_touch[session_id] = time.time()
                yield f"event: message\ndata: {msg}\n\n"
        finally:
            _sessions.pop(session_id, None)
            _session_touch.pop(session_id, None)
            logger.info("SSE session closed %s", session_id[:8])

    response = StreamingHttpResponse(
        event_stream(),
        content_type="text/event-stream",
    )
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"
    return response


@csrf_exempt
@require_POST
def messages(request: HttpRequest):
    """SSE message intake — client posts JSON-RPC; we forward to /mcp/."""
    session_id = request.GET.get("session_id")
    if not session_id:
        return JsonResponse({"error": "missing session_id"}, status=400)

    queue = _sessions.get(session_id)
    if queue is None:
        return JsonResponse({"error": "invalid or expired session"}, status=404)

    _session_touch[session_id] = time.time()

    try:
        body = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        return JsonResponse({"error": f"bad json: {e}"}, status=400)

    logger.info(
        "SSE message session=%s method=%s",
        session_id[:8],
        body.get("method", "?"),
    )

    result_text = _call_mcp(body)
    if result_text:
        queue.put(result_text)

    return JsonResponse({"status": "queued"}, status=202)


@csrf_exempt
def health(request: HttpRequest):
    return JsonResponse(
        {
            "status": "ok",
            "sessions": len(_sessions),
            "token_configured": bool(_token()),
            "target": _target_url(),
            "public_url": getattr(settings, "MCP_PUBLIC_URL", None) or None,
        }
    )
