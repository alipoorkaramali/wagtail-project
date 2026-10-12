from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="MCPBridgeSession",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("session_id", models.CharField(db_index=True, max_length=64, unique=True)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("last_seen", models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name="MCPBridgeMessage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("session_id", models.CharField(db_index=True, max_length=64)),
                ("payload", models.TextField()),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={"ordering": ["id"]},
        ),
        migrations.AddIndex(
            model_name="mcpbridgesession",
            index=models.Index(fields=["last_seen"], name="mcp_bridge__last_se_idx"),
        ),
        migrations.AddIndex(
            model_name="mcpbridgemessage",
            index=models.Index(fields=["session_id", "id"], name="mcp_bridge__session_idx"),
        ),
    ]
