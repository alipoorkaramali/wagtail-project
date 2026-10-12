# Generated migration for content snippets (priorities 5–10)
# Fixed: related_name accordion_panels (avoid conflict with Wagtail .panels)

import django.db.models.deletion
import modelcluster.fields
import wagtail.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0006_navbar_footer_ctabanner_alertbar"),
        ("wagtailimages", "0027_image_description"),
    ]

    operations = [
        migrations.CreateModel(
            name="Testimonial",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100, verbose_name="نام")),
                ("role", models.CharField(blank=True, help_text="مثلاً مدیرعامل شرکت فلان", max_length=120, verbose_name="سمت / شرکت")),
                ("quote", models.TextField(verbose_name="متن نظر")),
                ("rating", models.PositiveSmallIntegerField(default=5, help_text="عدد بین ۱ تا ۵", verbose_name="امتیاز (۱ تا ۵)")),
                ("is_featured", models.BooleanField(default=False, verbose_name="ویژه (نمایش در صفحه اصلی)")),
                ("photo", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="+", to="wagtailimages.image", verbose_name="عکس")),
            ],
            options={
                "verbose_name": "Testimonial / نظر مشتری",
                "verbose_name_plural": "نظرات مشتریان",
            },
        ),
        migrations.CreateModel(
            name="TeamMember",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100, verbose_name="نام")),
                ("role", models.CharField(max_length=120, verbose_name="سمت")),
                ("bio", models.TextField(blank=True, verbose_name="بیو کوتاه")),
                ("email", models.EmailField(blank=True, max_length=254, verbose_name="ایمیل")),
                ("linkedin", models.URLField(blank=True, verbose_name="لینکدین")),
                ("instagram", models.URLField(blank=True, verbose_name="اینستاگرام")),
                ("website", models.URLField(blank=True, verbose_name="وب‌سایت شخصی")),
                ("sort_order", models.PositiveIntegerField(default=0, help_text="عدد کوچک‌تر = بالاتر", verbose_name="ترتیب نمایش")),
                ("photo", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="+", to="wagtailimages.image", verbose_name="عکس")),
            ],
            options={
                "verbose_name": "Team Member / عضو تیم",
                "verbose_name_plural": "اعضای تیم",
                "ordering": ["sort_order", "name"],
            },
        ),
        migrations.CreateModel(
            name="Service",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=100, verbose_name="عنوان")),
                ("short_description", models.TextField(blank=True, verbose_name="توضیح کوتاه")),
                ("full_description", wagtail.fields.RichTextField(blank=True, verbose_name="توضیح کامل")),
                ("icon", models.CharField(blank=True, default="✦", help_text="مثلاً 🎨 یا 💻", max_length=50, verbose_name="آیکون (ایموجی)")),
                ("link_url", models.CharField(blank=True, max_length=255, verbose_name="لینک (صفحه جزئیات یا خارجی)")),
                ("is_featured", models.BooleanField(default=False, verbose_name="ویژه")),
                ("sort_order", models.PositiveIntegerField(default=0, verbose_name="ترتیب")),
                ("image", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="+", to="wagtailimages.image", verbose_name="تصویر")),
            ],
            options={
                "verbose_name": "Service / سرویس",
                "verbose_name_plural": "سرویس‌ها",
                "ordering": ["sort_order", "title"],
            },
        ),
        migrations.CreateModel(
            name="FAQItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("question", models.CharField(max_length=255, verbose_name="سوال")),
                ("answer", wagtail.fields.RichTextField(verbose_name="جواب")),
                ("category", models.CharField(blank=True, help_text="مثلاً عمومی، قیمت، پشتیبانی", max_length=80, verbose_name="دسته‌بندی")),
                ("sort_order", models.PositiveIntegerField(default=0, verbose_name="ترتیب")),
                ("is_active", models.BooleanField(default=True, verbose_name="فعال")),
            ],
            options={
                "verbose_name": "FAQ Item / سوال متداول",
                "verbose_name_plural": "سوالات متداول",
                "ordering": ["sort_order", "question"],
            },
        ),
        migrations.CreateModel(
            name="Accordion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(help_text="فقط برای شناسایی در ادمین", max_length=150, verbose_name="نام داخلی")),
                ("heading", models.CharField(blank=True, max_length=200, verbose_name="عنوان نمایشی (اختیاری)")),
                ("is_active", models.BooleanField(default=True, verbose_name="فعال")),
            ],
            options={
                "verbose_name": "Accordion / آکاردئون",
                "verbose_name_plural": "آکاردئون‌ها",
            },
        ),
        migrations.CreateModel(
            name="PartnerLogo",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(help_text="نام شرکت یا برند", max_length=100, verbose_name="نام")),
                ("website", models.URLField(blank=True, verbose_name="لینک وب‌سایت")),
                ("sort_order", models.PositiveIntegerField(default=0, verbose_name="ترتیب")),
                ("is_active", models.BooleanField(default=True, verbose_name="فعال")),
                ("logo", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="+", to="wagtailimages.image", verbose_name="لوگو")),
            ],
            options={
                "verbose_name": "Partner / Logo",
                "verbose_name_plural": "لوگوهای همکاران",
                "ordering": ["sort_order", "name"],
            },
        ),
        migrations.CreateModel(
            name="AccordionPanel",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("sort_order", models.IntegerField(blank=True, editable=False, null=True)),
                ("title", models.CharField(max_length=200, verbose_name="عنوان پنل")),
                ("content", wagtail.fields.RichTextField(verbose_name="محتوا")),
                ("is_open_by_default", models.BooleanField(default=False, verbose_name="باز به‌صورت پیش‌فرض")),
                (
                    "accordion",
                    modelcluster.fields.ParentalKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="accordion_panels",
                        to="home.accordion",
                    ),
                ),
            ],
            options={
                "ordering": ["sort_order"],
                "abstract": False,
            },
        ),
    ]
