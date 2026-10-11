from django.urls import path

from . import views

urlpatterns = [
    path("sse", views.sse, name="mcp_bridge_sse"),
    path("sse/", views.sse, name="mcp_bridge_sse_slash"),
    path("messages", views.messages, name="mcp_bridge_messages"),
    path("messages/", views.messages, name="mcp_bridge_messages_slash"),
    path("mcp-bridge/health", views.health, name="mcp_bridge_health"),
    path("mcp-bridge/health/", views.health, name="mcp_bridge_health_slash"),
]
