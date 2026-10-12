"""Shared MCP SSE session + message store (works across Gunicorn workers)."""
from django.db import models
from django.utils import timezone


class MCPBridgeSession(models.Model):
    session_id = models.CharField(max_length=64, unique=True, db_index=True)
    created_at = models.DateTimeField(default=timezone.now)
    last_seen = models.DateTimeField(default=timezone.now)

    class Meta:
        indexes = [
            models.Index(fields=["last_seen"]),
        ]


class MCPBridgeMessage(models.Model):
    session_id = models.CharField(max_length=64, db_index=True)
    payload = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["id"]
        indexes = [
            models.Index(fields=["session_id", "id"]),
        ]
