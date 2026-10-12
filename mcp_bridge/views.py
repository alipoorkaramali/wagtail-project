"""
MCP SSE bridge for Grok (URL-only connector).

Session IDs are signed (any worker validates). Message payloads use DB.
_call_mcp talks to wagtail-mcp over real HTTP with a hard timeout —
never Django's Test Client (nested client + gthread/SSE caused hangs).
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import time
import urllib.error
import urllib.request
from datetime import timedelta
from typing import List

from django.conf import settings
from django.core import signing
from django.http import HttpRequest, JsonResponse, StreamingHttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from mcp_bridge.models import MCPBridgeMessage

logger = logging.getLogger(__name__)

_SALT = "mcp-bridge-sse-v2"
_SESSION_MAX_AGE = 120
_MAX_SSE_SECONDS = 90
_POLL_EVERY = 1.0
_MCP_HTTP_TIMEOUT = 25  # seconds — fail fast so Grok does not hang forever


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


def _mcp_targets() -> List[str]:
    """Ordered list of /mcp/ URLs to try (first success wins)."""
    targets: List[str] = []
    configured = (getattr(settings, "MCP_TARGET_URL", None) or "").strip()
    if configured:
        targets.append(configured if configured.endswith("/") else configured + "/")

    port = os.environ.get("PORT") or os.environ.get("MCP_PORT") or "8000"
    targets.append(f"http://127.0.0.1:{port}/mcp/")

    public = (getattr(settings, "MCP_PUBLIC_URL", None) or "").rstrip("/")
    if public:
        targets.append(f"{public}/mcp/")

    # de-dupe preserve order
    seen = set()
    unique = []
    for t in targets:
        if t not in seen:
            seen.add(t)
            unique.append(t)
    return unique


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
    """POST JSON-RPC to wagtail-mcp via HTTP (timeout-bounded)."""
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

    payload = json.dumps(body).encode("utf-8")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }

    errors = []
    for url in _mcp_targets():
        try:
            req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=_MCP_HTTP_TIMEOUT) as resp:
                raw = resp.read().decode("utf-8", errors="replace")
                ct = resp.headers.get("Content-Type", "")
                status = getattr(resp, "status", 200)
                if status >= 400:
                    logger.warning("MCP HTTP %s from %s: %s", status, url, raw[:200])
                    errors.append(f"{url} -> HTTP {status}")
                    continue
                result = _parse_mcp_body(raw, ct)
                if result:
                    logger.info("MCP OK via %s method=%s", url, body.get("method", "?"))
                    return result
                errors.append(f"{url} -> empty body")
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="replace")[:200]
            logger.warning("MCP HTTPError %s %s: %s", e.code, url, err_body)
            errors.append(f"{url} -> HTTP {e.code}")
            # invalid token etc. — no point trying other targets with same token
            if e.code in (401, 403):
                return json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "id": body.get("id"),
                        "error": {
                            "code": -32001,
                            "message": f"MCP auth failed ({e.code}): {err_body}",
                        },
                    }
                )
        except Exception as e:
            logger.warning("MCP call failed %s: %s", url, e)
            errors.append(f"{url} -> {type(e).__name__}: {e}")

    return json.dumps(
        {
            "jsonrpc": "2.0",
            "id": body.get("id"),
            "error": {
                "code": -32603,
                "message": "MCP upstream failed: " + "; ".join(errors[:5]),
            },
        }
    )


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
                        time.sleep(_POLL_EVERY)
                except Exception:
                    logger.exception("SSE poll error")
                    yield ": ping\n\n"
                    time.sleep(_POLL_EVERY)
        finally:
            try:
                MCPBridgeMessage.objects.filter(session_id=key).delete()
            except Exception:
                pass
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
            "call_mode": "http",
            "mcp_timeout_seconds": _MCP_HTTP_TIMEOUT,
            "mcp_targets": _mcp_targets(),
            "sse_max_seconds": _MAX_SSE_SECONDS,
            "session_auth": "signed",
            "message_store": "database",
            "public_url": getattr(settings, "MCP_PUBLIC_URL", None) or None,
        }
    )
