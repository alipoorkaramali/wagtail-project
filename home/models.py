from django.db import models
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.models import Page, Orderable
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel
from wagtail.snippets.models import register_snippet
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock
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
        APIField("title", writable=True),
        APIField("description", writable=True),
        APIField("icon", writable=True),
    ]


# ──────────────────────────────────────────────
# SNIPPETS — Core (Navbar, Footer, CTA, Alert)
# ──────────────────────────────────────────────

@register_snippet
class Navbar(ClusterableModel):
    """منوی بالای سایت — شبیه Navbar در Wagtail CRX"""

    title = models.CharField(
        max_length=100,
        verbose_name="نام داخلی",
        help_text="فقط برای شناسایی در ادمین (مثلاً منوی اصلی)",
    )
    logo_text = models.CharField(
        max_length=80,
        blank=True,
        default="سایت من",
        verbose_name="متن لوگو",
    )
    logo_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="تصویر لوگو (اختیاری)",
    )
    cta_text = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="متن دکمه CTA در منو",
        help_text="مثلاً تماس بگیرید",
    )
    cta_link = models.URLField(
        blank=True,
        verbose_name="لینک دکمه CTA",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
        help_text="فقط یک Navbar فعال نمایش داده می‌شود",
    )

    panels = [
        FieldPanel("title"),
        MultiFieldPanel(
            [
                FieldPanel("logo_text"),
                FieldPanel("logo_image"),
            ],
            heading="لوگو",
        ),
        MultiFieldPanel(
            [
                FieldPanel("cta_text"),
                FieldPanel("cta_link"),
            ],
            heading="دکمه فراخوان (اختیاری)",
        ),
        FieldPanel("is_active"),
        InlinePanel("menu_items", label="آیتم منو", min_num=0),
    ]

    api_fields = [
        APIField("title", writable=True),
        APIField("logo_text", writable=True),
        APIField("logo_image", writable=True),
        APIField("cta_text", writable=True),
        APIField("cta_link", writable=True),
        APIField("is_active", writable=True),
        APIField("menu_items", writable=True),
    ]

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Navbar / منوی بالا"
        verbose_name_plural = "Navbarها"


class NavbarMenuItem(Orderable):
    navbar = ParentalKey(
        "home.Navbar",
        on_delete=models.CASCADE,
        related_name="menu_items",
    )
    label = models.CharField(max_length=60, verbose_name="عنوان لینک")
    link_url = models.CharField(
        max_length=255,
        verbose_name="آدرس لینک",
        help_text="می‌تواند نسبی باشد (مثلاً /about/) یا کامل",
    )
    open_in_new_tab = models.BooleanField(default=False, verbose_name="باز شدن در تب جدید")

    panels = [
        FieldPanel("label"),
        FieldPanel("link_url"),
        FieldPanel("open_in_new_tab"),
    ]

    api_fields = [
        APIField("label", writable=True),
        APIField("link_url", writable=True),
        APIField("open_in_new_tab", writable=True),
    ]


@register_snippet
class Footer(ClusterableModel):
    """فوتر پایین سایت"""

    title = models.CharField(
        max_length=100,
        verbose_name="نام داخلی",
        help_text="فقط برای شناسایی در ادمین",
    )
    copyright_text = models.CharField(
        max_length=200,
        blank=True,
        default="© ساخته‌شده با Wagtail + Grok",
        verbose_name="متن کپی‌رایت",
    )
    about_text = models.TextField(
        blank=True,
        verbose_name="متن کوتاه درباره (اختیاری)",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
        help_text="فقط یک Footer فعال نمایش داده می‌شود",
    )

    panels = [
        FieldPanel("title"),
        FieldPanel("copyright_text"),
        FieldPanel("about_text"),
        FieldPanel("is_active"),
        InlinePanel("footer_links", label="لینک فوتر", min_num=0),
        InlinePanel("social_links", label="شبکه اجتماعی", min_num=0),
    ]

    api_fields = [
        APIField("title", writable=True),
        APIField("copyright_text", writable=True),
        APIField("about_text", writable=True),
        APIField("is_active", writable=True),
        APIField("footer_links", writable=True),
        APIField("social_links", writable=True),
    ]

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Footer / فوتر"
        verbose_name_plural = "Footerها"


class FooterLink(Orderable):
    footer = ParentalKey(
        "home.Footer",
        on_delete=models.CASCADE,
        related_name="footer_links",
    )
    label = models.CharField(max_length=60, verbose_name="عنوان لینک")
    link_url = models.CharField(max_length=255, verbose_name="آدرس لینک")

    panels = [
        FieldPanel("label"),
        FieldPanel("link_url"),
    ]

    api_fields = [
        APIField("label", writable=True),
        APIField("link_url", writable=True),
    ]


class FooterSocialLink(Orderable):
    footer = ParentalKey(
        "home.Footer",
        on_delete=models.CASCADE,
        related_name="social_links",
    )
    platform = models.CharField(
        max_length=40,
        verbose_name="پلتفرم",
        help_text="مثلاً Instagram, LinkedIn, Telegram",
    )
    url = models.URLField(verbose_name="لینک")
    icon = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="آیکون (ایموجی یا کلاس)",
        help_text="مثلاً 📷 یا نام کلاس آیکون",
    )

    panels = [
        FieldPanel("platform"),
        FieldPanel("url"),
        FieldPanel("icon"),
    ]

    api_fields = [
        APIField("platform", writable=True),
        APIField("url", writable=True),
        APIField("icon", writable=True),
    ]


@register_snippet
class CTABanner(models.Model):
    """بنر فراخوان قابل استفاده مجدد (Call to Action)"""

    title = models.CharField(max_length=150, verbose_name="عنوان")
    text = models.TextField(blank=True, verbose_name="توضیح کوتاه")
    button_text = models.CharField(
        max_length=50,
        blank=True,
        default="تماس بگیرید",
        verbose_name="متن دکمه",
    )
    button_link = models.URLField(blank=True, verbose_name="لینک دکمه")
    background_style = models.CharField(
        max_length=20,
        choices=[
            ("dark", "تیره"),
            ("light", "روشن"),
            ("accent", "رنگی"),
        ],
        default="dark",
        verbose_name="سبک پس‌زمینه",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
    )

    panels = [
        FieldPanel("title"),
        FieldPanel("text"),
        FieldPanel("button_text"),
        FieldPanel("button_link"),
        FieldPanel("background_style"),
        FieldPanel("is_active"),
    ]

    api_fields = [
        APIField("title", writable=True),
        APIField("text", writable=True),
        APIField("button_text", writable=True),
        APIField("button_link", writable=True),
        APIField("background_style", writable=True),
        APIField("is_active", writable=True),
    ]

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "CTA Banner / بنر فراخوان"
        verbose_name_plural = "CTA Bannerها"


@register_snippet
class AlertBar(models.Model):
    """نوار اعلان بالای سایت (Notification / Alert Bar)"""

    message = models.CharField(
        max_length=250,
        verbose_name="پیام",
        help_text="متن کوتاه اعلان",
    )
    link_text = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="متن لینک (اختیاری)",
    )
    link_url = models.URLField(
        blank=True,
        verbose_name="آدرس لینک",
    )
    style = models.CharField(
        max_length=20,
        choices=[
            ("info", "اطلاعاتی (آبی)"),
            ("success", "موفقیت (سبز)"),
            ("warning", "هشدار (نارنجی)"),
            ("promo", "پیشنهاد ویژه (بنفش)"),
        ],
        default="info",
        verbose_name="سبک",
    )
    is_dismissible = models.BooleanField(
        default=True,
        verbose_name="قابل بستن توسط کاربر",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
        help_text="فقط یک Alert فعال در بالای سایت نمایش داده می‌شود",
    )

    panels = [
        FieldPanel("message"),
        FieldPanel("link_text"),
        FieldPanel("link_url"),
        FieldPanel("style"),
        FieldPanel("is_dismissible"),
        FieldPanel("is_active"),
    ]

    api_fields = [
        APIField("message", writable=True),
        APIField("link_text", writable=True),
        APIField("link_url", writable=True),
        APIField("style", writable=True),
        APIField("is_dismissible", writable=True),
        APIField("is_active", writable=True),
    ]

    def __str__(self):
        return self.message[:60]

    class Meta:
        verbose_name = "Alert Bar / نوار اعلان"
        verbose_name_plural = "Alert Barها"


# ──────────────────────────────────────────────
# HomePage
# ──────────────────────────────────────────────

class HomePage(Page):
    """صفحه اصلی — هیرو + سرویس‌ها + درباره + CTA + محتوای آزاد"""

    # ── Hero ──
    hero_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="عکس هیرو و پارالاکس",
        help_text="این عکس هم به‌عنوان پرتره هیرو و هم پس‌زمینه پارالاکس استفاده می‌شود. برای عوض کردن، Choose an image را بزنید.",
    )
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
                FieldPanel("hero_image"),
                FieldPanel("hero_title"),
                FieldPanel("hero_subtitle"),
                FieldPanel("hero_button_text"),
                FieldPanel("hero_button_link"),
            ],
            heading="بخش هیرو (عکس + متن + پارالاکس)",
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
        APIField("hero_title", writable=True),
        APIField("hero_subtitle", writable=True),
        APIField("hero_button_text", writable=True),
        APIField("hero_button_link", writable=True),
        APIField("hero_image", writable=True),
        APIField("about_title", writable=True),
        APIField("about_text", writable=True),
        APIField("services_title", writable=True),
        APIField("cta_title", writable=True),
        APIField("cta_text", writable=True),
        APIField("cta_button_text", writable=True),
        APIField("cta_button_link", writable=True),
        APIField("body", writable=True),
        APIField("services", writable=True),
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
        APIField("intro", writable=True),
        APIField("body", writable=True),
        APIField("featured_image", writable=True),
    ]

    class Meta:
        verbose_name = "صفحه استاندارد"
        verbose_name_plural = "صفحات استاندارد"
