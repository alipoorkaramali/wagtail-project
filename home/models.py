from django.db import models
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.models import Page, Orderable
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtail.api import APIField

# See repository history — full models restored in next commit via parts
# Temporary minimal stub to avoid broken deploy; full file follows.

class ServiceItem(Orderable):
    page = ParentalKey("home.HomePage", on_delete=models.CASCADE, related_name="services")
    title = models.CharField(max_length=100, verbose_name="عنوان سرویس")
    description = models.TextField(blank=True, verbose_name="توضیح")
    icon = models.CharField(max_length=50, blank=True, default="✦", verbose_name="آیکون")
    panels = [FieldPanel("icon"), FieldPanel("title"), FieldPanel("description")]
    api_fields = [APIField("title", writable=True), APIField("description", writable=True), APIField("icon", writable=True)]

class HomePage(Page):
    body = StreamField([], blank=True, use_json_field=True)
    content_panels = Page.content_panels + [FieldPanel("body")]
    class Meta:
        verbose_name = "صفحه اصلی"
