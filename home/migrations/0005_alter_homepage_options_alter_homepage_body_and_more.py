# Generated to sync models with migration state (makemigrations --check)

import django.db.models.deletion
import wagtail.fields
from django.db import migrations, models


_STREAM_BLOCK_LOOKUP = {
    0: (
        "wagtail.blocks.StructBlock",
        [[("text", 5), ("level", 6)]],
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
        [[("image", 8), ("caption", 9), ("alignment", 10)]],
        {
            "icon": "image",
            "label": "تصویر",
            "template": "home/blocks/image.html",
        },
    ),
    3: (
        "wagtail.blocks.StructBlock",
        [[("title", 13), ("text", 11), ("button_text", 14), ("button_link", 12)]],
        {
            "icon": "link",
            "label": "فراخوان به اقدام (CTA)",
            "template": "home/blocks/cta.html",
        },
    ),
    4: (
        "wagtail.blocks.StructBlock",
        [[("quote", 15), ("author", 16)]],
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
            "choices": [("h2", "H2"), ("h3", "H3"), ("h4", "H4")],
            "label": "سطح عنوان",
        },
    ),
    7: ("wagtail.blocks.RichTextBlock", (), {"label": "متن"}),
    8: ("wagtail.images.blocks.ImageChooserBlock", (), {"label": "تصویر"}),
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
    13: ("wagtail.blocks.CharBlock", (), {"label": "عنوان"}),
    14: ("wagtail.blocks.CharBlock", (), {"label": "متن دکمه"}),
    15: ("wagtail.blocks.TextBlock", (), {"label": "نقل‌قول"}),
    16: (
        "wagtail.blocks.CharBlock",
        (),
        {"label": "نویسنده", "required": False},
    ),
}

_STREAM_FIELDS = [
    ("heading", 0),
    ("paragraph", 1),
    ("image", 2),
    ("cta", 3),
    ("quote", 4),
]


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0004_overhaul_homepage_and_standardpage"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="homepage",
            options={
                "verbose_name": "صفحه اصلی",
                "verbose_name_plural": "صفحات اصلی",
            },
        ),
        migrations.AlterField(
            model_name="homepage",
            name="hero_image",
            field=models.ForeignKey(
                blank=True,
                help_text=(
                    "این عکس هم به‌عنوان پرتره هیرو و هم پس‌زمینه پارالاکس استفاده می‌شود. "
                    "برای عوض کردن، Choose an image را بزنید."
                ),
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="wagtailimages.image",
                verbose_name="عکس هیرو و پارالاکس",
            ),
        ),
        migrations.AlterField(
            model_name="homepage",
            name="body",
            field=wagtail.fields.StreamField(
                _STREAM_FIELDS,
                blank=True,
                block_lookup=_STREAM_BLOCK_LOOKUP,
                verbose_name="محتوای اضافی",
            ),
        ),
        migrations.AlterField(
            model_name="standardpage",
            name="body",
            field=wagtail.fields.StreamField(
                _STREAM_FIELDS,
                blank=True,
                block_lookup=_STREAM_BLOCK_LOOKUP,
                verbose_name="محتوا",
            ),
        ),
    ]
