# Generated migration for advanced snippets (11–15)

import django.db.models.deletion
import modelcluster.fields
import wagtail.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0007_testimonial_teammember_service_faqitem_accordion_partnerlogo"),
        ("wagtailimages", "0027_image_description"),
    ]

    operations = [
        migrations.CreateModel(
            name="HeroBanner",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=200, verbose_name="عنوان")),
                ("subtitle", wagtail.fields.RichTextField(blank=True, verbose_name="زیرعنوان")),
                ("button_text", models.CharField(blank=True, max_length=50, verbose_name="متن دکمه")),
                ("button_link", models.URLField(blank=True, verbose_name="لینک دکمه")),
                ("is_active", models.BooleanField(default=True, verbose_name="فعال")),
                ("background_image", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="+", to="wagtailimages.image", verbose_name="تصویر پس‌زمینه")),
            ],
            options={
                "verbose_name": "بنر هیرو",
                "verbose_name_plural": "بنرهای هیرو",
            },
        ),
        migrations.CreateModel(
            name="ContactInfo",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(help_text="مثلاً اطلاعات اصلی", max_length=100, verbose_name="نام داخلی")),
                ("phone", models.CharField(blank=True, max_length=40, verbose_name="تلفن")),
                ("email", models.EmailField(blank=True, max_length=254, verbose_name="ایمیل")),
                ("address", models.TextField(blank=True, verbose_name="آدرس")),
                ("map_embed_url", models.URLField(blank=True, verbose_name="لینک نقشه (اختیاری)")),
                ("working_hours", models.CharField(blank=True, max_length=120, verbose_name="ساعات کاری")),
                ("is_active", models.BooleanField(default=True, verbose_name="فعال")),
            ],
            options={
                "verbose_name": "اطلاعات تماس",
                "verbose_name_plural": "اطلاعات تماس",
            },
        ),
        migrations.CreateModel(
            name="SocialLink",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("platform", models.CharField(help_text="مثلاً Instagram, LinkedIn, Telegram", max_length=40, verbose_name="پلتفرم")),
                ("url", models.URLField(verbose_name="لینک")),
                ("icon", models.CharField(blank=True, help_text="مثلاً 📷", max_length=30, verbose_name="آیکون (ایموجی)")),
                ("sort_order", models.PositiveIntegerField(default=0, verbose_name="ترتیب")),
                ("is_active", models.BooleanField(default=True, verbose_name="فعال")),
            ],
            options={
                "verbose_name": "شبکه اجتماعی",
                "verbose_name_plural": "شبکه‌های اجتماعی",
                "ordering": ["sort_order", "platform"],
            },
        ),
        migrations.CreateModel(
            name="PricingPlan",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100, verbose_name="نام پلن")),
                ("price", models.CharField(help_text="مثلاً ۲٬۵۰۰٬۰۰۰ تومان", max_length=50, verbose_name="قیمت")),
                ("period", models.CharField(blank=True, default="ماهانه", help_text="مثلاً ماهانه، سالانه، یک‌بار", max_length=40, verbose_name="دوره")),
                ("description", models.TextField(blank=True, verbose_name="توضیح کوتاه")),
                ("button_text", models.CharField(blank=True, default="شروع کنید", max_length=50, verbose_name="متن دکمه")),
                ("button_link", models.URLField(blank=True, verbose_name="لینک دکمه")),
                ("is_featured", models.BooleanField(default=False, verbose_name="ویژه (برجسته)")),
                ("sort_order", models.PositiveIntegerField(default=0, verbose_name="ترتیب")),
                ("is_active", models.BooleanField(default=True, verbose_name="فعال")),
            ],
            options={
                "verbose_name": "پلن قیمت",
                "verbose_name_plural": "پلن‌های قیمت",
                "ordering": ["sort_order", "name"],
            },
        ),
        migrations.CreateModel(
            name="Feature",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=120, verbose_name="عنوان")),
                ("description", models.TextField(blank=True, verbose_name="توضیح")),
                ("icon", models.CharField(blank=True, default="✦", max_length=50, verbose_name="آیکون (ایموجی)")),
                ("sort_order", models.PositiveIntegerField(default=0, verbose_name="ترتیب")),
                ("is_active", models.BooleanField(default=True, verbose_name="فعال")),
                ("image", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="+", to="wagtailimages.image", verbose_name="تصویر (اختیاری)")),
            ],
            options={
                "verbose_name": "ویژگی",
                "verbose_name_plural": "ویژگی‌ها",
                "ordering": ["sort_order", "title"],
            },
        ),
        migrations.CreateModel(
            name="PricingFeature",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("sort_order", models.IntegerField(blank=True, editable=False, null=True)),
                ("text", models.CharField(max_length=200, verbose_name="متن ویژگی")),
                ("is_included", models.BooleanField(default=True, verbose_name="شامل این پلن است")),
                ("plan", modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name="features", to="home.pricingplan")),
            ],
            options={
                "ordering": ["sort_order"],
                "abstract": False,
            },
        ),
    ]
