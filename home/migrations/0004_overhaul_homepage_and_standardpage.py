# Generated manually by Grok — complete home app overhaul

import django.db.models.deletion
import modelcluster.fields
import wagtail.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0003_homepage_body_homepage_hero_button_link_and_more"),
        ("wagtailcore", "0095_groupsitepermission"),
        ("wagtailimages", "0027_image_description"),
    ]

    operations = [
        # ── New fields on HomePage ──
        migrations.AddField(
            model_name="homepage",
            name="about_title",
            field=models.CharField(
                blank=True,
                default="درباره من",
                max_length=150,
                verbose_name="عنوان بخش درباره",
            ),
        ),
        migrations.AddField(
            model_name="homepage",
            name="about_text",
            field=wagtail.fields.RichTextField(
                blank=True, verbose_name="متن درباره"
            ),
        ),
        migrations.AddField(
            model_name="homepage",
            name="services_title",
            field=models.CharField(
                blank=True,
                default="خدمات",
                max_length=150,
                verbose_name="عنوان بخش خدمات",
            ),
        ),
        migrations.AddField(
            model_name="homepage",
            name="cta_title",
            field=models.CharField(
                blank=True,
                default="آماده شروع پروژه هستی؟",
                max_length=150,
                verbose_name="عنوان CTA",
            ),
        ),
        migrations.AddField(
            model_name="homepage",
            name="cta_text",
            field=models.TextField(blank=True, verbose_name="متن CTA"),
        ),
        migrations.AddField(
            model_name="homepage",
            name="cta_button_text",
            field=models.CharField(
                blank=True,
                default="تماس بگیرید",
                max_length=50,
                verbose_name="متن دکمه CTA",
            ),
        ),
        migrations.AddField(
            model_name="homepage",
            name="cta_button_link",
            field=models.URLField(blank=True, verbose_name="لینک دکمه CTA"),
        ),
        # ── Alter existing body StreamField to richer blocks ──
        migrations.AlterField(
            model_name="homepage",
            name="body",
            field=wagtail.fields.StreamField(
                [
                    ("heading", 0),
                    ("paragraph", 1),
                    ("image", 2),
                    ("cta", 3),
                    ("quote", 4),
                ],
                blank=True,
                block_lookup={
                    0: (
                        "wagtail.blocks.StructBlock",
                        [
                            [
                                ("text", 5),
                                ("level", 6),
                            ]
                        ],
                        {
                            "icon": "title",
                            "label": "عنوان",
                            "template": "home/blocks/heading.html",
                        },
                    ),
                    1: (
                        "wagtail.blocks.StructBlock",
                        [[("text", 7)]],
                        {
                            "icon": "pilcrow",
                            "label": "پاراگراف",
                            "template": "home/blocks/paragraph.html",
                        },
                    ),
                    2: (
                        "wagtail.blocks.StructBlock",
                        [
                            [
                                ("image", 8),
                                ("caption", 9),
                                ("alignment", 10),
                            ]
                        ],
                        {
                            "icon": "image",
                            "label": "تصویر",
                            "template": "home/blocks/image.html",
                        },
                    ),
                    3: (
                        "wagtail.blocks.StructBlock",
                        [
                            [
                                ("title", 5),
                                ("text", 11),
                                ("button_text", 5),
                                ("button_link", 12),
                            ]
                        ],
                        {
                            "icon": "link",
                            "label": "فراخوان به اقدام (CTA)",
                            "template": "home/blocks/cta.html",
                        },
                    ),
                    4: (
                        "wagtail.blocks.StructBlock",
                        [
                            [
                                ("quote", 11),
                                ("author", 9),
                            ]
                        ],
                        {
                            "icon": "openquote",
                            "label": "نقل‌قول",
                            "template": "home/blocks/quote.html",
                        },
                    ),
                    5: ("wagtail.blocks.CharBlock", (), {"label": "متن عنوان"}),
                    6: (
                        "wagtail.blocks.ChoiceBlock",
                        [],
                        {
                            "choices": [
                                ("h2", "H2"),
                                ("h3", "H3"),
                                ("h4", "H4"),
                            ],
                            "label": "سطح عنوان",
                        },
                    ),
                    7: ("wagtail.blocks.RichTextBlock", (), {"label": "متن"}),
                    8: (
                        "wagtail.images.blocks.ImageChooserBlock",
                        (),
                        {"label": "تصویر"},
                    ),
                    9: (
                        "wagtail.blocks.CharBlock",
                        (),
                        {"label": "توضیح تصویر", "required": False},
                    ),
                    10: (
                        "wagtail.blocks.ChoiceBlock",
                        [],
                        {
                            "choices": [
                                ("full", "تمام‌عرض"),
                                ("left", "چپ"),
                                ("right", "راست"),
                                ("center", "وسط"),
                            ],
                            "label": "تراز",
                        },
                    ),
                    11: (
                        "wagtail.blocks.TextBlock",
                        (),
                        {"label": "توضیح", "required": False},
                    ),
                    12: ("wagtail.blocks.URLBlock", (), {"label": "لینک دکمه"}),
                },
                verbose_name="محتوای اضافی",
            ),
        ),
        # ── Alter hero_button_text default ──
        migrations.AlterField(
            model_name="homepage",
            name="hero_button_text",
            field=models.CharField(
                blank=True,
                default="رزرو تماس",
                max_length=50,
                verbose_name="متن دکمه",
            ),
        ),
        # ── ServiceItem orderable ──
        migrations.CreateModel(
            name="ServiceItem",
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
                    "sort_order",
                    models.IntegerField(blank=True, editable=False, null=True),
                ),
                (
                    "title",
                    models.CharField(max_length=100, verbose_name="عنوان سرویس"),
                ),
                (
                    "description",
                    models.TextField(blank=True, verbose_name="توضیح"),
                ),
                (
                    "icon",
                    models.CharField(
                        blank=True,
                        default="✦",
                        help_text="مثلاً 🎨 یا 💻",
                        max_length=50,
                        verbose_name="آیکون (ایموجی یا متن کوتاه)",
                    ),
                ),
                (
                    "page",
                    modelcluster.fields.ParentalKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="services",
                        to="home.homepage",
                    ),
                ),
            ],
            options={
                "ordering": ["sort_order"],
                "abstract": False,
            },
        ),
        # ── StandardPage ──
        migrations.CreateModel(
            name="StandardPage",
            fields=[
                (
                    "page_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="wagtailcore.page",
                    ),
                ),
                (
                    "intro",
                    wagtail.fields.RichTextField(
                        blank=True, verbose_name="مقدمه"
                    ),
                ),
                (
                    "body",
                    wagtail.fields.StreamField(
                        [
                            ("heading", 0),
                            ("paragraph", 1),
                            ("image", 2),
                            ("cta", 3),
                            ("quote", 4),
                        ],
                        blank=True,
                        block_lookup={
                            0: (
                                "wagtail.blocks.StructBlock",
                                [
                                    [
                                        ("text", 5),
                                        ("level", 6),
                                    ]
                                ],
                                {
                                    "icon": "title",
                                    "label": "عنوان",
                                    "template": "home/blocks/heading.html",
                                },
                            ),
                            1: (
                                "wagtail.blocks.StructBlock",
                                [[("text", 7)]],
                                {
                                    "icon": "pilcrow",
                                    "label": "پاراگراف",
                                    "template": "home/blocks/paragraph.html",
                                },
                            ),
                            2: (
                                "wagtail.blocks.StructBlock",
                                [
                                    [
                                        ("image", 8),
                                        ("caption", 9),
                                        ("alignment", 10),
                                    ]
                                ],
                                {
                                    "icon": "image",
                                    "label": "تصویر",
                                    "template": "home/blocks/image.html",
                                },
                            ),
                            3: (
                                "wagtail.blocks.StructBlock",
                                [
                                    [
                                        ("title", 5),
                                        ("text", 11),
                                        ("button_text", 5),
                                        ("button_link", 12),
                                    ]
                                ],
                                {
                                    "icon": "link",
                                    "label": "فراخوان به اقدام (CTA)",
                                    "template": "home/blocks/cta.html",
                                },
                            ),
                            4: (
                                "wagtail.blocks.StructBlock",
                                [
                                    [
                                        ("quote", 11),
                                        ("author", 9),
                                    ]
                                ],
                                {
                                    "icon": "openquote",
                                    "label": "نقل‌قول",
                                    "template": "home/blocks/quote.html",
                                },
                            ),
                            5: (
                                "wagtail.blocks.CharBlock",
                                (),
                                {"label": "متن عنوان"},
                            ),
                            6: (
                                "wagtail.blocks.ChoiceBlock",
                                [],
                                {
                                    "choices": [
                                        ("h2", "H2"),
                                        ("h3", "H3"),
                                        ("h4", "H4"),
                                    ],
                                    "label": "سطح عنوان",
                                },
                            ),
                            7: (
                                "wagtail.blocks.RichTextBlock",
                                (),
                                {"label": "متن"},
                            ),
                            8: (
                                "wagtail.images.blocks.ImageChooserBlock",
                                (),
                                {"label": "تصویر"},
                            ),
                            9: (
                                "wagtail.blocks.CharBlock",
                                (),
                                {"label": "توضیح تصویر", "required": False},
                            ),
                            10: (
                                "wagtail.blocks.ChoiceBlock",
                                [],
                                {
                                    "choices": [
                                        ("full", "تمام‌عرض"),
                                        ("left", "چپ"),
                                        ("right", "راست"),
                                        ("center", "وسط"),
                                    ],
                                    "label": "تراز",
                                },
                            ),
                            11: (
                                "wagtail.blocks.TextBlock",
                                (),
                                {"label": "توضیح", "required": False},
                            ),
                            12: (
                                "wagtail.blocks.URLBlock",
                                (),
                                {"label": "لینک دکمه"},
                            ),
                        },
                        verbose_name="محتوا",
                    ),
                ),
                (
                    "featured_image",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="wagtailimages.image",
                        verbose_name="تصویر شاخص",
                    ),
                ),
            ],
            options={
                "verbose_name": "صفحه استاندارد",
                "verbose_name_plural": "صفحات استاندارد",
            },
            bases=("wagtailcore.page",),
        ),
    ]
