"""
MCP SSE bridge for Grok (URL-only connector).

_call_mcp: RequestFactory + resolve, Accept application/json (no self-HTTP).
SSE: closes DB connection while sleeping so other threads can use the pool.
messages: runs MCP work then queues result (must complete on a free worker/thread).
"""
from __future__ import annotations

import hashlib
import json
import logging
import time
from datetime import timedelta

from django.conf import settings
from django.core import signing
from django.db import connection
from django.http import HttpRequest, JsonResponse, StreamingHttpResponse
from django.test import RequestFactory
from django.urls import resolve
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from mcp_bridge.models import MCPBridgeMessage

logger = logging.getLogger(__name__)

_SALT = "mcp-bridge-sse-v2"
_SESSION_MAX_AGE = 120
_MAX_SSE_SECONDS = 90
_POLL_EVERY = 1.0
_MAX_BODY_BYTES = 512_000


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


def _make_session_id() -> str:
    return signing.dumps({"v": 2, "ts": int(time.time())}, salt=_SALT)


def _valid_session_id(session_id: str) -> bool:
    try:
        signing.loads(session_id, salt=_SALT, max_age=_SESSION_MAX_AGE)
        return True
    except signing.BadSignature:
        return False


def _msg_key(session_id: str) -> str:
    return hashlib.sha256(session_id.encode("utf-8")).hexdigest()


def _consume_response(response) -> tuple[int, str, str]:
    status = getattr(response, "status_code", 200)
    ct = ""
    if hasattr(response, "headers"):
        ct = response.headers.get("Content-Type", "") or ""
    elif hasattr(response, "get"):
        ct = response.get("Content-Type", "") or ""

    if hasattr(response, "streaming_content"):
        parts = []
        total = 0
        try:
            for chunk in response.streaming_content:
                if isinstance(chunk, bytes):
                    piece = chunk.decode("utf-8", errors="replace")
                else:
                    piece = str(chunk)
                parts.append(piece)
                total += len(piece)
                joined = "".join(parts)
                if total >= _MAX_BODY_BYTES:
                    break
                if "text/event-stream" in (ct or "").lower():
                    if joined.count("\n\n") >= 1 or joined.count("\r\n\r\n") >= 1:
                        break
                else:
                    s = joined.strip()
                    if s.startswith("{") and s.endswith("}"):
                        try:
                            json.loads(s)
                            break
                        except json.JSONDecodeError:
                            pass
        finally:
            closer = getattr(response, "close", None)
            if callable(closer):
                try:
                    closer()
                except Exception:
                    pass
        raw = "".join(parts)
    else:
        content = getattr(response, "content", b"") or b""
        raw = content.decode("utf-8", errors="replace") if isinstance(content, bytes) else str(content)
    return status, raw, ct


def _parse_mcp_body(raw: str, content_type: str) -> str:
    ct = (content_type or "").lower()
    if "text/event-stream" in ct:
        chunks = []
        for line in raw.splitlines():
            if line.startswith("data:"):
                payload = line[5:].strip()
                if payload:
                    chunks.append(payload)
        return chunks[-1] if chunks else raw.strip()
    return raw.strip()


def _call_mcp(body: dict) -> str:
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
        factory = RequestFactory()
        request = factory.post(
            "/mcp/",
            data=json.dumps(body),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
            HTTP_ACCEPT="application/json",
        )
        match = resolve("/mcp/")
        response = match.func(request, *match.args, **match.kwargs)
        if not hasattr(response, "status_code") and callable(response):
            response = response(request)
        status, raw, ct = _consume_response(response)
    except Exception as e:
        logger.exception("MCP in-process view call failed")
        return json.dumps(
            {
                "jsonrpc": "2.0",
                "id": body.get("id"),
                "error": {"code": -32603, "message": f"in-process error: {e}"},
            }
        )

    if status >= 400:
        logger.warning("MCP view HTTP %s: %s", status, raw[:300])
        return json.dumps(
            {
                "jsonrpc": "2.0",
                "id": body.get("id"),
                "error": {
                    "code": -32001,
                    "message": f"MCP returned HTTP {status}: {raw[:200]}",
                },
            }
        )

    result = _parse_mcp_body(raw, ct)
    logger.info(
        "MCP OK method=%s status=%s bytes=%s",
        body.get("method", "?"),
        status,
        len(result),
    )
    return result


def _purge_old_messages() -> None:
    cutoff = timezone.now() - timedelta(seconds=_SESSION_MAX_AGE + 30)
    deleted, _ = MCPBridgeMessage.objects.filter(created_at__lt=cutoff).delete()
    if deleted:
        logger.info("Purged %s old MCP bridge messages", deleted)


@csrf_exempt
@require_GET
def sse(request: HttpRequest):
    _purge_old_messages()
    token = _token()
    if not token:
        return JsonResponse(
            {"error": "MCP_TOKEN is not set. Add it in CodeRed environment variables."},
            status=503,
        )

    session_id = _make_session_id()
    key = _msg_key(session_id)
    base = _public_base(request)
    endpoint_url = f"{base}/messages/?session_id={session_id}"
    logger.info("SSE session start key=%s...", key[:12])

    def event_stream():
        yield f"event: endpoint\ndata: {endpoint_url}\n\n"
        deadline = time.time() + _MAX_SSE_SECONDS
        try:
            while time.time() < deadline:
                try:
                    rows = list(
                        MCPBridgeMessage.objects.filter(session_id=key).order_by("id")[:20]
                    )
                    if rows:
                        ids = [r.id for r in rows]
                        for row in rows:
                            yield f"event: message\ndata: {row.payload}\n\n"
                        MCPBridgeMessage.objects.filter(id__in=ids).delete()
                    else:
                        yield ": ping\n\n"
                        # Release DB connection while sleeping so other
                        # workers/threads can use the pool
                        connection.close()
                        time.sleep(_POLL_EVERY)
                except Exception:
                    logger.exception("SSE poll error")
                    connection.close()
                    yield ": ping\n\n"
                    time.sleep(_POLL_EVERY)
        finally:
            try:
                MCPBridgeMessage.objects.filter(session_id=key).delete()
            except Exception:
                pass
            connection.close()
            logger.info("SSE session closed key=%s...", key[:12])

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
    session_id = request.GET.get("session_id")
    if not session_id:
        return JsonResponse({"error": "missing session_id"}, status=400)

    if not _valid_session_id(session_id):
        return JsonResponse({"error": "invalid or expired session"}, status=404)

    try:
        body = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        return JsonResponse({"error": f"bad json: {e}"}, status=400)

    logger.info("SSE message method=%s", body.get("method", "?"))

    result_text = _call_mcp(body)
    if result_text:
        MCPBridgeMessage.objects.create(
            session_id=_msg_key(session_id),
            payload=result_text,
        )

    return JsonResponse({"status": "queued"}, status=202)


@csrf_exempt
def health(request: HttpRequest):
    _purge_old_messages()
    return JsonResponse(
        {
            "status": "ok",
            "token_configured": bool(_token()),
            "call_mode": "request_factory_json",
            "sse_max_seconds": _MAX_SSE_SECONDS,
            "session_auth": "signed",
            "message_store": "database",
            "public_url": getattr(settings, "MCP_PUBLIC_URL", None) or None,
        }
    )
