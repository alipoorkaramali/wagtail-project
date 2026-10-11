"""
In-process MCP bridge for Grok (URL-only connector, no Bearer in UI).

Grok ──GET /sse──▶ bridge ──(+ MCP_TOKEN)──▶ /mcp/  (same Django process)

IMPORTANT on CodeRed (few WSGI workers):
  A long-lived SSE stream holds one worker for the whole connection.
  We hard-cap session length and concurrent streams so the site
  cannot stay offline (CR504) when Grok or bots open /sse.
"""
from __future__ import annotations

import json
import logging
import time
import uuid
from queue import Empty, Queue

from django.conf import settings
from django.http import HttpRequest, JsonResponse, StreamingHttpResponse
from django.test import Client
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

logger = logging.getLogger(__name__)

_sessions: dict[str, Queue] = {}
_session_touch: dict[str, float] = {}

# Keep CodeRed responsive: short streams, few concurrent sessions.
_SESSION_TTL = 90
_MAX_SSE_SECONDS = 45
_MAX_CONCURRENT_SSE = 1
_PING_EVERY = 5


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


def _cleanup_stale() -> None:
    now = time.time()
    stale = [sid for sid, ts in _session_touch.items() if now - ts > _SESSION_TTL]
    for sid in stale:
        q = _sessions.pop(sid, None)
        _session_touch.pop(sid, None)
        if q is not None:
            try:
                q.put_nowait(None)
            except Exception:
                pass


def _call_mcp(body: dict) -> str:
    """POST JSON-RPC to wagtail-mcp in-process (no outbound HTTP)."""
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

    try:
        client = Client()
        response = client.post(
            "/mcp/",
            data=json.dumps(body),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
            HTTP_ACCEPT="application/json, text/event-stream",
        )
    except Exception as e:
        logger.exception("MCP in-process call failed")
        return json.dumps(
            {
                "jsonrpc": "2.0",
                "id": body.get("id"),
                "error": {"code": -32603, "message": f"in-process error: {e}"},
            }
        )

    raw = response.content.decode("utf-8", errors="replace")
    content_type = response.get("Content-Type", "") or ""

    if response.status_code >= 400:
        logger.warning(
            "MCP in-process HTTP %s: %s",
            response.status_code,
            raw[:300],
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
    """Legacy MCP SSE — capped so it cannot monopolize CodeRed workers."""
    _cleanup_stale()
    token = _token()
    if not token:
        return JsonResponse(
            {"error": "MCP_TOKEN is not set. Add it in CodeRed environment variables."},
            status=503,
        )

    if len(_sessions) >= _MAX_CONCURRENT_SSE:
        return JsonResponse(
            {
                "error": "SSE capacity full",
                "detail": "Another MCP session is active. Retry in under a minute.",
            },
            status=503,
        )

    session_id = str(uuid.uuid4())
    msg_queue: Queue = Queue()
    _sessions[session_id] = msg_queue
    _session_touch[session_id] = time.time()

    base = _public_base(request)
    endpoint_url = f"{base}/messages/?session_id={session_id}"
    logger.info("SSE session %s endpoint=%s", session_id[:8], endpoint_url)

    def event_stream():
        yield f"event: endpoint\ndata: {endpoint_url}\n\n"
        deadline = time.time() + _MAX_SSE_SECONDS
        try:
            while time.time() < deadline:
                try:
                    msg = msg_queue.get(timeout=_PING_EVERY)
                except Empty:
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
    """SSE message intake — JSON-RPC → /mcp/ in-process."""
    session_id = request.GET.get("session_id")
    if not session_id:
        return JsonResponse({"error": "missing session_id"}, status=400)

    msg_queue = _sessions.get(session_id)
    if msg_queue is None:
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
        msg_queue.put(result_text)

    return JsonResponse({"status": "queued"}, status=202)


@csrf_exempt
def health(request: HttpRequest):
    return JsonResponse(
        {
            "status": "ok",
            "sessions": len(_sessions),
            "token_configured": bool(_token()),
            "target": "in-process:/mcp/",
            "sse_max_seconds": _MAX_SSE_SECONDS,
            "sse_max_concurrent": _MAX_CONCURRENT_SSE,
            "public_url": getattr(settings, "MCP_PUBLIC_URL", None) or None,
        }
    )
