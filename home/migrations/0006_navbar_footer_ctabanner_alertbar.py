# Generated migration for core Snippets

import django.db.models.deletion
import modelcluster.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0005_alter_homepage_options_alter_homepage_body_and_more"),
        ("wagtailimages", "0027_image_description"),
    ]

    operations = [
        migrations.CreateModel(
            name="AlertBar",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("message", models.CharField(help_text="متن کوتاه اعلان", max_length=250, verbose_name="پیام")),
                ("link_text", models.CharField(blank=True, max_length=50, verbose_name="متن لینک (اختیاری)")),
                ("link_url", models.URLField(blank=True, verbose_name="آدرس لینک")),
                (
                    "style",
                    models.CharField(
                        choices=[
                            ("info", "اطلاعاتی (آبی)"),
                            ("success", "موفقیت (سبز)"),
                            ("warning", "هشدار (نارنجی)"),
                            ("promo", "پیشنهاد ویژه (بنفش)"),
                        ],
                        default="info",
                        max_length=20,
                        verbose_name="سبک",
                    ),
                ),
                ("is_dismissible", models.BooleanField(default=True, verbose_name="قابل بستن توسط کاربر")),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="فقط یک Alert فعال در بالای سایت نمایش داده می‌شود",
                        verbose_name="فعال",
                    ),
                ),
            ],
            options={
                "verbose_name": "Alert Bar / نوار اعلان",
                "verbose_name_plural": "Alert Barها",
            },
        ),
        migrations.CreateModel(
            name="CTABanner",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=150, verbose_name="عنوان")),
                ("text", models.TextField(blank=True, verbose_name="توضیح کوتاه")),
                (
                    "button_text",
                    models.CharField(
                        blank=True, default="تماس بگیرید", max_length=50, verbose_name="متن دکمه"
                    ),
                ),
                ("button_link", models.URLField(blank=True, verbose_name="لینک دکمه")),
                (
                    "background_style",
                    models.CharField(
                        choices=[
                            ("dark", "تیره"),
                            ("light", "روشن"),
                            ("accent", "رنگی"),
                        ],
                        default="dark",
                        max_length=20,
                        verbose_name="سبک پس‌زمینه",
                    ),
                ),
                ("is_active", models.BooleanField(default=True, verbose_name="فعال")),
            ],
            options={
                "verbose_name": "CTA Banner / بنر فراخوان",
                "verbose_name_plural": "CTA Bannerها",
            },
        ),
        migrations.CreateModel(
            name="Footer",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "title",
                    models.CharField(
                        help_text="فقط برای شناسایی در ادمین", max_length=100, verbose_name="نام داخلی"
                    ),
                ),
                (
                    "copyright_text",
                    models.CharField(
                        blank=True,
                        default="© ساخته‌شده با Wagtail + Grok",
                        max_length=200,
                        verbose_name="متن کپی‌رایت",
                    ),
                ),
                ("about_text", models.TextField(blank=True, verbose_name="متن کوتاه درباره (اختیاری)")),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="فقط یک Footer فعال نمایش داده می‌شود",
                        verbose_name="فعال",
                    ),
                ),
            ],
            options={
                "verbose_name": "Footer / فوتر",
                "verbose_name_plural": "Footerها",
            },
        ),
        migrations.CreateModel(
            name="Navbar",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "title",
                    models.CharField(
                        help_text="فقط برای شناسایی در ادمین (مثلاً منوی اصلی)",
                        max_length=100,
                        verbose_name="نام داخلی",
                    ),
                ),
                (
                    "logo_text",
                    models.CharField(
                        blank=True, default="سایت من", max_length=80, verbose_name="متن لوگو"
                    ),
                ),
                (
                    "cta_text",
                    models.CharField(
                        blank=True,
                        help_text="مثلاً تماس بگیرید",
                        max_length=50,
                        verbose_name="متن دکمه CTA در منو",
                    ),
                ),
                ("cta_link", models.URLField(blank=True, verbose_name="لینک دکمه CTA")),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="فقط یک Navbar فعال نمایش داده می‌شود",
                        verbose_name="فعال",
                    ),
                ),
                (
                    "logo_image",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="wagtailimages.image",
                        verbose_name="تصویر لوگو (اختیاری)",
                    ),
                ),
            ],
            options={
                "verbose_name": "Navbar / منوی بالا",
                "verbose_name_plural": "Navbarها",
            },
        ),
        migrations.CreateModel(
            name="NavbarMenuItem",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("sort_order", models.IntegerField(blank=True, editable=False, null=True)),
                ("label", models.CharField(max_length=60, verbose_name="عنوان لینک")),
                (
                    "link_url",
                    models.CharField(
                        help_text="می‌تواند نسبی باشد (مثلاً /about/) یا کامل",
                        max_length=255,
                        verbose_name="آدرس لینک",
                    ),
                ),
                ("open_in_new_tab", models.BooleanField(default=False, verbose_name="باز شدن در تب جدید")),
                (
                    "navbar",
                    modelcluster.fields.ParentalKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="menu_items",
                        to="home.navbar",
                    ),
                ),
            ],
            options={
                "ordering": ["sort_order"],
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="FooterSocialLink",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("sort_order", models.IntegerField(blank=True, editable=False, null=True)),
                (
                    "platform",
                    models.CharField(
                        help_text="مثلاً Instagram, LinkedIn, Telegram",
                        max_length=40,
                        verbose_name="پلتفرم",
                    ),
                ),
                ("url", models.URLField(verbose_name="لینک")),
                (
                    "icon",
                    models.CharField(
                        blank=True,
                        help_text="مثلاً 📷 یا نام کلاس آیکون",
                        max_length=30,
                        verbose_name="آیکون (ایموجی یا کلاس)",
                    ),
                ),
                (
                    "footer",
                    modelcluster.fields.ParentalKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="social_links",
                        to="home.footer",
                    ),
                ),
            ],
            options={
                "ordering": ["sort_order"],
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="FooterLink",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("sort_order", models.IntegerField(blank=True, editable=False, null=True)),
                ("label", models.CharField(max_length=60, verbose_name="عنوان لینک")),
                ("link_url", models.CharField(max_length=255, verbose_name="آدرس لینک")),
                (
                    "footer",
                    modelcluster.fields.ParentalKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="footer_links",
                        to="home.footer",
                    ),
                ),
            ],
            options={
                "ordering": ["sort_order"],
                "abstract": False,
            },
        ),
    ]
