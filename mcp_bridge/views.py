"""
In-process MCP bridge for Grok (URL-only connector).

Grok ──GET /sse──▶ bridge ──(+ MCP_TOKEN)──▶ /mcp/  (same Django app)

Design goals (CodeRed / few workers):
  - Session + message queue in the DATABASE so any Gunicorn worker can
    serve /sse and /messages (no sticky in-memory state).
  - Only one concurrent SSE session (one Grok is enough).
  - Hard time-cap on SSE so a stuck client cannot hold a worker forever.
  - Site stays responsive via gthread workers (see Dockerfile).
"""
from __future__ import annotations

import json
import logging
import time
import uuid
from datetime import timedelta

from django.conf import settings
from django.http import HttpRequest, JsonResponse, StreamingHttpResponse
from django.test import Client
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from mcp_bridge.models import MCPBridgeMessage, MCPBridgeSession

logger = logging.getLogger(__name__)

# Tuned for: 1 Grok user, site must not go down
_SESSION_TTL_SECONDS = 120
_MAX_SSE_SECONDS = 60
_MAX_CONCURRENT_SSE = 1
_POLL_EVERY = 1.5


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
    cutoff = timezone.now() - timedelta(seconds=_SESSION_TTL_SECONDS)
    stale_ids = list(
        MCPBridgeSession.objects.filter(last_seen__lt=cutoff).values_list("session_id", flat=True)
    )
    if not stale_ids:
        return
    MCPBridgeMessage.objects.filter(session_id__in=stale_ids).delete()
    MCPBridgeSession.objects.filter(session_id__in=stale_ids).delete()
    logger.info("MCP bridge cleaned %s stale sessions", len(stale_ids))


def _active_session_count() -> int:
    cutoff = timezone.now() - timedelta(seconds=_SESSION_TTL_SECONDS)
    return MCPBridgeSession.objects.filter(last_seen__gte=cutoff).count()


def _call_mcp(body: dict) -> str:
    """POST JSON-RPC to wagtail-mcp in-process (injects MCP_TOKEN)."""
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
        logger.warning("MCP in-process HTTP %s: %s", response.status_code, raw[:300])

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
    """Legacy MCP SSE — DB-backed, time-capped, single concurrent session."""
    _cleanup_stale()
    token = _token()
    if not token:
        return JsonResponse(
            {"error": "MCP_TOKEN is not set. Add it in CodeRed environment variables."},
            status=503,
        )

    if _active_session_count() >= _MAX_CONCURRENT_SSE:
        return JsonResponse(
            {
                "error": "SSE capacity full",
                "detail": "One MCP session is already active. Retry in under a minute.",
            },
            status=503,
        )

    session_id = str(uuid.uuid4())
    MCPBridgeSession.objects.create(session_id=session_id)

    base = _public_base(request)
    endpoint_url = f"{base}/messages/?session_id={session_id}"
    logger.info("SSE session %s endpoint=%s", session_id[:8], endpoint_url)

    def event_stream():
        yield f"event: endpoint\ndata: {endpoint_url}\n\n"
        deadline = time.time() + _MAX_SSE_SECONDS
        try:
            while time.time() < deadline:
                # Touch session so TTL does not expire mid-stream
                MCPBridgeSession.objects.filter(session_id=session_id).update(
                    last_seen=timezone.now()
                )
                rows = list(
                    MCPBridgeMessage.objects.filter(session_id=session_id).order_by("id")[:20]
                )
                if rows:
                    ids = [r.id for r in rows]
                    for row in rows:
                        yield f"event: message\ndata: {row.payload}\n\n"
                    MCPBridgeMessage.objects.filter(id__in=ids).delete()
                else:
                    yield ": ping\n\n"
                    time.sleep(_POLL_EVERY)
        finally:
            MCPBridgeMessage.objects.filter(session_id=session_id).delete()
            MCPBridgeSession.objects.filter(session_id=session_id).delete()
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
    """SSE message intake — any worker can handle (DB session lookup)."""
    session_id = request.GET.get("session_id")
    if not session_id:
        return JsonResponse({"error": "missing session_id"}, status=400)

    _cleanup_stale()
    session = MCPBridgeSession.objects.filter(session_id=session_id).first()
    if session is None:
        return JsonResponse({"error": "invalid or expired session"}, status=404)

    MCPBridgeSession.objects.filter(pk=session.pk).update(last_seen=timezone.now())

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
        MCPBridgeMessage.objects.create(session_id=session_id, payload=result_text)

    return JsonResponse({"status": "queued"}, status=202)


@csrf_exempt
def health(request: HttpRequest):
    _cleanup_stale()
    return JsonResponse(
        {
            "status": "ok",
            "sessions": _active_session_count(),
            "token_configured": bool(_token()),
            "target": "in-process:/mcp/",
            "sse_max_seconds": _MAX_SSE_SECONDS,
            "sse_max_concurrent": _MAX_CONCURRENT_SSE,
            "session_store": "database",
            "public_url": getattr(settings, "MCP_PUBLIC_URL", None) or None,
        }
    )
