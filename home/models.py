from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.models import Page, Orderable
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtail.api import APIField
from django.utils.translation import gettext_lazy as _

# Import all snippets so Django discovers them
from home.snippet_models import *  # noqa: F401,F403


class HeadingBlock(blocks.StructBlock):
    text = blocks.CharBlock(label=_("Heading text"))
    level = blocks.ChoiceBlock(choices=[("h2", "H2"), ("h3", "H3"), ("h4", "H4")], default="h2", label=_("Level"))

    class Meta:
        icon = "title"
        label = _("Heading")
        template = "home/blocks/heading.html"


class ParagraphBlock(blocks.StructBlock):
    text = blocks.RichTextBlock(label=_("Text"))

    class Meta:
        icon = "pilcrow"
        label = _("Paragraph")
        template = "home/blocks/paragraph.html"


class ImageBlock(blocks.StructBlock):
    image = ImageChooserBlock(label=_("Image"))
    caption = blocks.CharBlock(required=False, label=_("Caption"))
    alignment = blocks.ChoiceBlock(
        choices=[("full", _("Full width")), ("left", _("Left")), ("right", _("Right")), ("center", _("Center"))],
        default="full",
        label=_("Alignment"),
    )

    class Meta:
        icon = "image"
        label = _("Image")
        template = "home/blocks/image.html"


class CallToActionBlock(blocks.StructBlock):
    title = blocks.CharBlock(label=_("Title"))
    text = blocks.TextBlock(required=False, label=_("Text"))
    button_text = blocks.CharBlock(label=_("Button text"))
    button_link = blocks.URLBlock(label=_("Button link"))

    class Meta:
        icon = "link"
        label = _("Call to Action")
        template = "home/blocks/cta.html"


class QuoteBlock(blocks.StructBlock):
    quote = blocks.TextBlock(label=_("Quote"))
    author = blocks.CharBlock(required=False, label=_("Author"))

    class Meta:
        icon = "openquote"
        label = _("Quote")
        template = "home/blocks/quote.html"


class BaseStreamBlock(blocks.StreamBlock):
    heading = HeadingBlock()
    paragraph = ParagraphBlock()
    image = ImageBlock()
    cta = CallToActionBlock()
    quote = QuoteBlock()


class ServiceItem(Orderable):
    page = ParentalKey("home.HomePage", on_delete=models.CASCADE, related_name="services")
    title = models.CharField(max_length=100, verbose_name=_("Service title"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    icon = models.CharField(max_length=50, blank=True, default="✦", verbose_name=_("Icon"))
    panels = [FieldPanel("icon"), FieldPanel("title"), FieldPanel("description")]
    api_fields = [
        APIField("title", writable=True),
        APIField("description", writable=True),
        APIField("icon", writable=True),
    ]


class HomePage(Page):
    hero_image = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+", verbose_name=_("Hero image")
    )
    hero_title = models.CharField(max_length=200, blank=True, verbose_name=_("Hero title"))
    hero_subtitle = RichTextField(blank=True, verbose_name=_("Hero subtitle"))
    hero_button_text = models.CharField(max_length=50, blank=True, default="Book a call", verbose_name=_("Hero button text"))
    hero_button_link = models.URLField(blank=True, verbose_name=_("Hero button link"))
    about_title = models.CharField(max_length=150, blank=True, default="About me", verbose_name=_("About title"))
    about_text = RichTextField(blank=True, verbose_name=_("About text"))
    services_title = models.CharField(max_length=150, blank=True, default="Services", verbose_name=_("Services title"))
    cta_title = models.CharField(max_length=150, blank=True, default="Ready to start?", verbose_name=_("CTA title"))
    cta_text = models.TextField(blank=True, verbose_name=_("CTA text"))
    cta_button_text = models.CharField(max_length=50, blank=True, default="Contact us", verbose_name=_("CTA button text"))
    cta_button_link = models.URLField(blank=True, verbose_name=_("CTA button link"))
    body = StreamField(BaseStreamBlock(), blank=True, use_json_field=True, verbose_name=_("Body"))

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [FieldPanel("hero_image"), FieldPanel("hero_title"), FieldPanel("hero_subtitle"), FieldPanel("hero_button_text"), FieldPanel("hero_button_link")],
            heading=_("Hero"),
        ),
        MultiFieldPanel([FieldPanel("about_title"), FieldPanel("about_text")], heading=_("About")),
        MultiFieldPanel(
            [FieldPanel("services_title"), InlinePanel("services", label=_("Service"), min_num=0, max_num=8)],
            heading=_("Services"),
        ),
        MultiFieldPanel(
            [FieldPanel("cta_title"), FieldPanel("cta_text"), FieldPanel("cta_button_text"), FieldPanel("cta_button_link")],
            heading=_("CTA"),
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
        verbose_name = _("Home Page")
        verbose_name_plural = _("Home Pages")


class StandardPage(Page):
    intro = RichTextField(blank=True, verbose_name=_("Intro"))
    body = StreamField(BaseStreamBlock(), blank=True, use_json_field=True, verbose_name=_("Body"))
    featured_image = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+", verbose_name=_("Featured image")
    )
    content_panels = Page.content_panels + [FieldPanel("intro"), FieldPanel("featured_image"), FieldPanel("body")]
    api_fields = [APIField("intro", writable=True), APIField("body", writable=True), APIField("featured_image", writable=True)]

    class Meta:
        verbose_name = _("Standard Page")
        verbose_name_plural = _("Standard Pages")
