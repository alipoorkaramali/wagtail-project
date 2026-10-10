from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock


class HomePage(Page):
    # بخش هیرو
    hero_title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="عنوان اصلی",
        help_text="مثال: طراح وب‌سایت و گرافیست"
    )
    hero_subtitle = RichTextField(
        blank=True,
        verbose_name="توضیحات کوتاه"
    )
    hero_button_text = models.CharField(
        max_length=50,
        blank=True,
        default="Book A Call",
        verbose_name="متن دکمه"
    )
    hero_button_link = models.URLField(
        blank=True,
        verbose_name="لینک دکمه"
    )
    hero_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="تصویر هیرو"
    )

    # محتوای آزاد پایین صفحه (برای بعد)
    body = StreamField([
        ("heading", blocks.CharBlock(form_classname="title", label="عنوان")),
        ("paragraph", blocks.RichTextBlock(label="متن")),
        ("image", ImageChooserBlock(label="تصویر")),
    ], blank=True, use_json_field=True, verbose_name="محتوای اضافی")

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel("hero_title"),
            FieldPanel("hero_subtitle"),
            FieldPanel("hero_button_text"),
            FieldPanel("hero_button_link"),
            FieldPanel("hero_image"),
        ], heading="بخش هیرو (بالای صفحه)"),
        FieldPanel("body"),
    ]