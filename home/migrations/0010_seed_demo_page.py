# Create a published StandardPage explaining demo snippets

from django.db import migrations
from django.utils import timezone


def seed_page(apps, schema_editor):
    ContentType = apps.get_model("contenttypes", "ContentType")
    Page = apps.get_model("wagtailcore", "Page")
    StandardPage = apps.get_model("home", "StandardPage")

    if StandardPage.objects.filter(slug="demo-snippets").exists():
        return

    home = Page.objects.filter(depth=2).order_by("path").first()
    if home is None:
        return

    # Build page via tree API if available on historical model
    ct = ContentType.objects.get_for_model(StandardPage)
    intro = (
        "<p><strong>صفحه تست اسنیپت‌ها</strong></p>"
        "<p>این صفحه برای بررسی Snippets ساخته شده است.</p>"
        "<ul>"
        "<li>بالای سایت: <em>Alert Bar</em> و <em>Navbar</em> (اسنیپت site-wide)</li>"
        "<li>پایین سایت: <em>Footer</em></li>"
        "<li>در ادمین → Snippets: Testimonial, FAQ, Pricing, Team, Service و بقیه نمونه‌ها</li>"
        "</ul>"
        "<p>نمونه داده‌ها با migration seed شده‌اند (مثلاً Demo Navbar، Sara Ahmadi، پلن Starter).</p>"
    )

    page = StandardPage(
        title="Demo Snippets",
        slug="demo-snippets",
        intro=intro,
        body=[],
        content_type_id=ct.id,
        locale_id=home.locale_id,
        live=True,
        has_unpublished_changes=False,
        first_published_at=timezone.now(),
        last_published_at=timezone.now(),
        latest_revision_created_at=timezone.now(),
    )
    try:
        home.add_child(instance=page)
    except Exception:
        # Fallback: skip if tree API unavailable on historical model
        return

    # Ensure live
    StandardPage.objects.filter(id=page.id).update(live=True)


def unseed(apps, schema_editor):
    StandardPage = apps.get_model("home", "StandardPage")
    StandardPage.objects.filter(slug="demo-snippets").delete()


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0009_seed_demo_snippets_page"),
    ]

    operations = [
        migrations.RunPython(seed_page, unseed),
    ]
