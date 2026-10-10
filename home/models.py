from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.models import Page, Orderable
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtail.images.models import Image
from wagtail.api import APIField


# ──────────────────────────────────────────────
# Reusable StreamField blocks
# ──────────────────────────────────────────────

class HeadingBlock(blocks.StructBlock):
    text = blocks.CharBlock(label="متن عنوان")
    level = blocks.ChoiceBlock(
        choices=[
            ("h2", "H2"),
            ("h3", "H3"),
            ("h4", "H4"),
        ],
        default="h2",
        label="سطح عنوان",
    )

    class Meta:
        icon = "title"
        label = "عنوان"
        template = "home/blocks/heading.html"


class ParagraphBlock(blocks.StructBlock):
    text = blocks.RichTextBlock(label="متن")

    class Meta:
        icon = "pilcrow"
        label = "پاراگراف"
        template = "home/blocks/paragraph.html"


class ImageBlock(blocks.StructBlock):
    image = ImageChooserBlock(label="تصویر")
    caption = blocks.CharBlock(required=False, label="توضیح تصویر")
    alignment = blocks.ChoiceBlock(
        choices=[
            ("full", "تمام‌عرض"),
            ("left", "چپ"),
            ("right", "راست"),
            ("center", "وسط"),
        ],
        default="full",
        label="تراز",
    )

    class Meta:
        icon = "image"
        label = "تصویر"
        template = "home/blocks/image.html"


class CallToActionBlock(blocks.StructBlock):
    title = blocks.CharBlock(label="عنوان")
    text = blocks.TextBlock(required=False, label="توضیح")
    button_text = blocks.CharBlock(label="متن دکمه")
    button_link = blocks.URLBlock(label="لینک دکمه")

    class Meta:
        icon = "link"
        label = "فراخوان به اقدام (CTA)"
        template = "home/blocks/cta.html"


class QuoteBlock(blocks.StructBlock):
    quote = blocks.TextBlock(label="نقل‌قول")
    author = blocks.CharBlock(required=False, label="نویسنده")

    class Meta:
        icon = "openquote"
        label = "نقل‌قول"
        template = "home/blocks/quote.html"


class BaseStreamBlock(blocks.StreamBlock):
    """Shared stream blocks used across page types."""
    heading = HeadingBlock()
    paragraph = ParagraphBlock()
    image = ImageBlock()
    cta = CallToActionBlock()
    quote = QuoteBlock()


# ──────────────────────────────────────────────
# Orderable: Service items for HomePage
# ──────────────────────────────────────────────

class ServiceItem(Orderable):
    page = ParentalKey(
        "home.HomePage",
        on_delete=models.CASCADE,
        related_name="services",
    )
    title = models.CharField(max_length=100, verbose_name="عنوان سرویس")
    description = models.TextField(blank=True, verbose_name="توضیح")
    icon = models.CharField(
        max_length=50,
        blank=True,
        default="✦",
        verbose_name="آیکون (ایموجی یا متن کوتاه)",
        help_text="مثلاً 🎨 یا 💻",
    )

    panels = [
        FieldPanel("icon"),
        FieldPanel("title"),
        FieldPanel("description"),
    ]

    api_fields = [
        APIField("title"),
        APIField("description"),
        APIField("icon"),
    ]


# ──────────────────────────────────────────────
# HomePage
# ──────────────────────────────────────────────

class HomePage(Page):
    """صفحه اصلی — هیرو + سرویس‌ها + درباره + CTA + محتوای آزاد"""

    # ── Hero ──
    hero_title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="عنوان اصلی",
        help_text="مثال: طراح وب‌سایت و گرافیست",
    )
    hero_subtitle = RichTextField(
        blank=True,
        verbose_name="توضیحات کوتاه",
    )
    hero_button_text = models.CharField(
        max_length=50,
        blank=True,
        default="رزرو تماس",
        verbose_name="متن دکمه",
    )
    hero_button_link = models.URLField(
        blank=True,
        verbose_name="لینک دکمه",
    )
    hero_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="تصویر هیرو",
    )

    # ── About section ──
    about_title = models.CharField(
        max_length=150,
        blank=True,
        default="درباره من",
        verbose_name="عنوان بخش درباره",
    )
    about_text = RichTextField(
        blank=True,
        verbose_name="متن درباره",
    )

    # ── Services section heading ──
    services_title = models.CharField(
        max_length=150,
        blank=True,
        default="خدمات",
        verbose_name="عنوان بخش خدمات",
    )

    # ── Final CTA ──
    cta_title = models.CharField(
        max_length=150,
        blank=True,
        default="آماده شروع پروژه هستی؟",
        verbose_name="عنوان CTA",
    )
    cta_text = models.TextField(
        blank=True,
        verbose_name="متن CTA",
    )
    cta_button_text = models.CharField(
        max_length=50,
        blank=True,
        default="تماس بگیرید",
        verbose_name="متن دکمه CTA",
    )
    cta_button_link = models.URLField(
        blank=True,
        verbose_name="لینک دکمه CTA",
    )

    # ── Free-form body ──
    body = StreamField(
        BaseStreamBlock(),
        blank=True,
        use_json_field=True,
        verbose_name="محتوای اضافی",
    )

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("hero_title"),
                FieldPanel("hero_subtitle"),
                FieldPanel("hero_button_text"),
                FieldPanel("hero_button_link"),
                FieldPanel("hero_image"),
            ],
            heading="بخش هیرو",
        ),
        MultiFieldPanel(
            [
                FieldPanel("about_title"),
                FieldPanel("about_text"),
            ],
            heading="بخش درباره",
        ),
        MultiFieldPanel(
            [
                FieldPanel("services_title"),
                InlinePanel("services", label="سرویس", min_num=0, max_num=8),
            ],
            heading="بخش خدمات",
        ),
        MultiFieldPanel(
            [
                FieldPanel("cta_title"),
                FieldPanel("cta_text"),
                FieldPanel("cta_button_text"),
                FieldPanel("cta_button_link"),
            ],
            heading="فراخوان نهایی (CTA)",
        ),
        FieldPanel("body"),
    ]

    api_fields = [
        APIField("hero_title"),
        APIField("hero_subtitle"),
        APIField("hero_button_text"),
        APIField("hero_button_link"),
        APIField("hero_image"),
        APIField("about_title"),
        APIField("about_text"),
        APIField("services_title"),
        APIField("cta_title"),
        APIField("cta_text"),
        APIField("cta_button_text"),
        APIField("cta_button_link"),
        APIField("body"),
        APIField("services"),
    ]

    class Meta:
        verbose_name = "صفحه اصلی"
        verbose_name_plural = "صفحات اصلی"


# ──────────────────────────────────────────────
# StandardPage — generic content page
# ──────────────────────────────────────────────

class StandardPage(Page):
    """صفحه استاندارد برای محتوای عمومی (درباره، تماس، و غیره)"""

    intro = RichTextField(
        blank=True,
        verbose_name="مقدمه",
    )
    body = StreamField(
        BaseStreamBlock(),
        blank=True,
        use_json_field=True,
        verbose_name="محتوا",
    )
    featured_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="تصویر شاخص",
    )

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("featured_image"),
        FieldPanel("body"),
    ]

    api_fields = [
        APIField("intro"),
        APIField("body"),
        APIField("featured_image"),
    ]

    class Meta:
        verbose_name = "صفحه استاندارد"
        verbose_name_plural = "صفحات استاندارد"
