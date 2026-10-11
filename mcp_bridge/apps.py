from django.apps import AppConfig


class McpBridgeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "mcp_bridge"
    verbose_name = "MCP Bridge (Grok / SSE)"
