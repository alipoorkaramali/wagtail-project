"""
All reusable Snippet models.
Labels use gettext_lazy so they follow admin language (en / fa).
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.models import Orderable
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel
from wagtail.api import APIField


class Navbar(ClusterableModel):
    title = models.CharField(max_length=100, verbose_name=_("Internal name"), help_text=_("Only for identification in admin"))
    logo_text = models.CharField(max_length=80, blank=True, default="My Site", verbose_name=_("Logo text"))
    logo_image = models.ForeignKey("wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+", verbose_name=_("Logo image"))
    cta_text = models.CharField(max_length=50, blank=True, verbose_name=_("CTA button text"))
    cta_link = models.URLField(blank=True, verbose_name=_("CTA button link"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"), help_text=_("Only one active Navbar is shown"))

    panels = [
        FieldPanel("title"),
        MultiFieldPanel([FieldPanel("logo_text"), FieldPanel("logo_image")], heading=_("Logo")),
        MultiFieldPanel([FieldPanel("cta_text"), FieldPanel("cta_link")], heading=_("CTA button")),
        FieldPanel("is_active"),
        InlinePanel("menu_items", label=_("Menu item"), min_num=0),
    ]
    api_fields = [
        APIField("title", writable=True), APIField("logo_text", writable=True),
        APIField("logo_image", writable=True), APIField("cta_text", writable=True),
        APIField("cta_link", writable=True), APIField("is_active", writable=True),
        APIField("menu_items", writable=True),
    ]

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Navbar")
        verbose_name_plural = _("Navbars")


class NavbarMenuItem(Orderable):
    navbar = ParentalKey("home.Navbar", on_delete=models.CASCADE, related_name="menu_items")
    label = models.CharField(max_length=60, verbose_name=_("Link label"))
    link_url = models.CharField(max_length=255, verbose_name=_("Link URL"), help_text=_("Relative or absolute URL"))
    open_in_new_tab = models.BooleanField(default=False, verbose_name=_("Open in new tab"))
    panels = [FieldPanel("label"), FieldPanel("link_url"), FieldPanel("open_in_new_tab")]
    api_fields = [APIField("label", writable=True), APIField("link_url", writable=True), APIField("open_in_new_tab", writable=True)]


class Footer(ClusterableModel):
    title = models.CharField(max_length=100, verbose_name=_("Internal name"))
    copyright_text = models.CharField(max_length=200, blank=True, default="© Built with Wagtail", verbose_name=_("Copyright text"))
    about_text = models.TextField(blank=True, verbose_name=_("Short about text"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    panels = [
        FieldPanel("title"), FieldPanel("copyright_text"), FieldPanel("about_text"), FieldPanel("is_active"),
        InlinePanel("footer_links", label=_("Footer link"), min_num=0),
        InlinePanel("social_links", label=_("Social link"), min_num=0),
    ]
    api_fields = [
        APIField("title", writable=True), APIField("copyright_text", writable=True),
        APIField("about_text", writable=True), APIField("is_active", writable=True),
        APIField("footer_links", writable=True), APIField("social_links", writable=True),
    ]

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Footer")
        verbose_name_plural = _("Footers")


class FooterLink(Orderable):
    footer = ParentalKey("home.Footer", on_delete=models.CASCADE, related_name="footer_links")
    label = models.CharField(max_length=60, verbose_name=_("Link label"))
    link_url = models.CharField(max_length=255, verbose_name=_("Link URL"))
    panels = [FieldPanel("label"), FieldPanel("link_url")]
    api_fields = [APIField("label", writable=True), APIField("link_url", writable=True)]


class FooterSocialLink(Orderable):
    footer = ParentalKey("home.Footer", on_delete=models.CASCADE, related_name="social_links")
    platform = models.CharField(max_length=40, verbose_name=_("Platform"), help_text=_("e.g. Instagram, LinkedIn"))
    url = models.URLField(verbose_name=_("URL"))
    icon = models.CharField(max_length=30, blank=True, verbose_name=_("Icon"))
    panels = [FieldPanel("platform"), FieldPanel("url"), FieldPanel("icon")]
    api_fields = [APIField("platform", writable=True), APIField("url", writable=True), APIField("icon", writable=True)]


class CTABanner(models.Model):
    title = models.CharField(max_length=150, verbose_name=_("Title"))
    text = models.TextField(blank=True, verbose_name=_("Short text"))
    button_text = models.CharField(max_length=50, blank=True, default="Contact us", verbose_name=_("Button text"))
    button_link = models.URLField(blank=True, verbose_name=_("Button link"))
    background_style = models.CharField(
        max_length=20,
        choices=[("dark", _("Dark")), ("light", _("Light")), ("accent", _("Accent"))],
        default="dark", verbose_name=_("Background style"),
    )
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    panels = [FieldPanel("title"), FieldPanel("text"), FieldPanel("button_text"), FieldPanel("button_link"), FieldPanel("background_style"), FieldPanel("is_active")]
    api_fields = [APIField("title", writable=True), APIField("text", writable=True), APIField("button_text", writable=True), APIField("button_link", writable=True), APIField("background_style", writable=True), APIField("is_active", writable=True)]

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("CTA Banner")
        verbose_name_plural = _("CTA Banners")


class AlertBar(models.Model):
    message = models.CharField(max_length=250, verbose_name=_("Message"))
    link_text = models.CharField(max_length=50, blank=True, verbose_name=_("Link text"))
    link_url = models.URLField(blank=True, verbose_name=_("Link URL"))
    style = models.CharField(
        max_length=20,
        choices=[("info", _("Info")), ("success", _("Success")), ("warning", _("Warning")), ("promo", _("Promo"))],
        default="info", verbose_name=_("Style"),
    )
    is_dismissible = models.BooleanField(default=True, verbose_name=_("Dismissible"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    panels = [FieldPanel("message"), FieldPanel("link_text"), FieldPanel("link_url"), FieldPanel("style"), FieldPanel("is_dismissible"), FieldPanel("is_active")]
    api_fields = [APIField("message", writable=True), APIField("link_text", writable=True), APIField("link_url", writable=True), APIField("style", writable=True), APIField("is_dismissible", writable=True), APIField("is_active", writable=True)]

    def __str__(self):
        return self.message[:60]

    class Meta:
        verbose_name = _("Alert Bar")
        verbose_name_plural = _("Alert Bars")


class Testimonial(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    role = models.CharField(max_length=120, blank=True, verbose_name=_("Role / Company"))
    quote = models.TextField(verbose_name=_("Quote"))
    photo = models.ForeignKey("wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+", verbose_name=_("Photo"))
    rating = models.PositiveSmallIntegerField(default=5, verbose_name=_("Rating (1–5)"))
    is_featured = models.BooleanField(default=False, verbose_name=_("Featured"))
    panels = [FieldPanel("name"), FieldPanel("role"), FieldPanel("quote"), FieldPanel("photo"), FieldPanel("rating"), FieldPanel("is_featured")]
    api_fields = [APIField("name", writable=True), APIField("role", writable=True), APIField("quote", writable=True), APIField("photo", writable=True), APIField("rating", writable=True), APIField("is_featured", writable=True)]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Testimonial")
        verbose_name_plural = _("Testimonials")


class TeamMember(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    role = models.CharField(max_length=120, verbose_name=_("Role"))
    bio = models.TextField(blank=True, verbose_name=_("Short bio"))
    photo = models.ForeignKey("wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+", verbose_name=_("Photo"))
    email = models.EmailField(blank=True, verbose_name=_("Email"))
    linkedin = models.URLField(blank=True, verbose_name=_("LinkedIn"))
    instagram = models.URLField(blank=True, verbose_name=_("Instagram"))
    website = models.URLField(blank=True, verbose_name=_("Website"))
    sort_order = models.PositiveIntegerField(default=0, verbose_name=_("Sort order"))
    panels = [
        FieldPanel("name"), FieldPanel("role"), FieldPanel("bio"), FieldPanel("photo"),
        MultiFieldPanel([FieldPanel("email"), FieldPanel("linkedin"), FieldPanel("instagram"), FieldPanel("website")], heading=_("Contact")),
        FieldPanel("sort_order"),
    ]
    api_fields = [APIField("name", writable=True), APIField("role", writable=True), APIField("bio", writable=True), APIField("photo", writable=True), APIField("email", writable=True), APIField("linkedin", writable=True), APIField("instagram", writable=True), APIField("website", writable=True), APIField("sort_order", writable=True)]

    def __str__(self):
        return f"{self.name} ({self.role})"

    class Meta:
        verbose_name = _("Team Member")
        verbose_name_plural = _("Team Members")
        ordering = ["sort_order", "name"]


class Service(models.Model):
    title = models.CharField(max_length=100, verbose_name=_("Title"))
    short_description = models.TextField(blank=True, verbose_name=_("Short description"))
    full_description = RichTextField(blank=True, verbose_name=_("Full description"))
    icon = models.CharField(max_length=50, blank=True, default="✦", verbose_name=_("Icon"))
    image = models.ForeignKey("wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+", verbose_name=_("Image"))
    link_url = models.CharField(max_length=255, blank=True, verbose_name=_("Link URL"))
    is_featured = models.BooleanField(default=False, verbose_name=_("Featured"))
    sort_order = models.PositiveIntegerField(default=0, verbose_name=_("Sort order"))
    panels = [FieldPanel("title"), FieldPanel("icon"), FieldPanel("short_description"), FieldPanel("full_description"), FieldPanel("image"), FieldPanel("link_url"), FieldPanel("is_featured"), FieldPanel("sort_order")]
    api_fields = [APIField("title", writable=True), APIField("short_description", writable=True), APIField("full_description", writable=True), APIField("icon", writable=True), APIField("image", writable=True), APIField("link_url", writable=True), APIField("is_featured", writable=True), APIField("sort_order", writable=True)]

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Service")
        verbose_name_plural = _("Services")
        ordering = ["sort_order", "title"]


class FAQItem(models.Model):
    question = models.CharField(max_length=255, verbose_name=_("Question"))
    answer = RichTextField(verbose_name=_("Answer"))
    category = models.CharField(max_length=80, blank=True, verbose_name=_("Category"))
    sort_order = models.PositiveIntegerField(default=0, verbose_name=_("Sort order"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    panels = [FieldPanel("question"), FieldPanel("answer"), FieldPanel("category"), FieldPanel("sort_order"), FieldPanel("is_active")]
    api_fields = [APIField("question", writable=True), APIField("answer", writable=True), APIField("category", writable=True), APIField("sort_order", writable=True), APIField("is_active", writable=True)]

    def __str__(self):
        return self.question[:80]

    class Meta:
        verbose_name = _("FAQ Item")
        verbose_name_plural = _("FAQ Items")
        ordering = ["sort_order", "question"]


class Accordion(ClusterableModel):
    title = models.CharField(max_length=150, verbose_name=_("Internal name"))
    heading = models.CharField(max_length=200, blank=True, verbose_name=_("Display heading"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    panels = [
        FieldPanel("title"), FieldPanel("heading"), FieldPanel("is_active"),
        InlinePanel("accordion_panels", label=_("Panel"), min_num=1),
    ]
    api_fields = [APIField("title", writable=True), APIField("heading", writable=True), APIField("is_active", writable=True), APIField("accordion_panels", writable=True)]

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Accordion")
        verbose_name_plural = _("Accordions")


class AccordionPanel(Orderable):
    accordion = ParentalKey("home.Accordion", on_delete=models.CASCADE, related_name="accordion_panels")
    title = models.CharField(max_length=200, verbose_name=_("Panel title"))
    content = RichTextField(verbose_name=_("Content"))
    is_open_by_default = models.BooleanField(default=False, verbose_name=_("Open by default"))
    panels = [FieldPanel("title"), FieldPanel("content"), FieldPanel("is_open_by_default")]
    api_fields = [APIField("title", writable=True), APIField("content", writable=True), APIField("is_open_by_default", writable=True)]


class PartnerLogo(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    logo = models.ForeignKey("wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+", verbose_name=_("Logo"))
    website = models.URLField(blank=True, verbose_name=_("Website"))
    sort_order = models.PositiveIntegerField(default=0, verbose_name=_("Sort order"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    panels = [FieldPanel("name"), FieldPanel("logo"), FieldPanel("website"), FieldPanel("sort_order"), FieldPanel("is_active")]
    api_fields = [APIField("name", writable=True), APIField("logo", writable=True), APIField("website", writable=True), APIField("sort_order", writable=True), APIField("is_active", writable=True)]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Partner Logo")
        verbose_name_plural = _("Partner Logos")
        ordering = ["sort_order", "name"]


class HeroBanner(models.Model):
    title = models.CharField(max_length=200, verbose_name=_("Title"))
    subtitle = RichTextField(blank=True, verbose_name=_("Subtitle"))
    background_image = models.ForeignKey("wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+", verbose_name=_("Background image"))
    button_text = models.CharField(max_length=50, blank=True, verbose_name=_("Button text"))
    button_link = models.URLField(blank=True, verbose_name=_("Button link"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    panels = [FieldPanel("title"), FieldPanel("subtitle"), FieldPanel("background_image"), FieldPanel("button_text"), FieldPanel("button_link"), FieldPanel("is_active")]
    api_fields = [APIField("title", writable=True), APIField("subtitle", writable=True), APIField("background_image", writable=True), APIField("button_text", writable=True), APIField("button_link", writable=True), APIField("is_active", writable=True)]

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Hero Banner")
        verbose_name_plural = _("Hero Banners")


class ContactInfo(models.Model):
    title = models.CharField(max_length=100, verbose_name=_("Internal name"))
    phone = models.CharField(max_length=40, blank=True, verbose_name=_("Phone"))
    email = models.EmailField(blank=True, verbose_name=_("Email"))
    address = models.TextField(blank=True, verbose_name=_("Address"))
    map_embed_url = models.URLField(blank=True, verbose_name=_("Map URL"))
    working_hours = models.CharField(max_length=120, blank=True, verbose_name=_("Working hours"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    panels = [FieldPanel("title"), FieldPanel("phone"), FieldPanel("email"), FieldPanel("address"), FieldPanel("map_embed_url"), FieldPanel("working_hours"), FieldPanel("is_active")]
    api_fields = [APIField("title", writable=True), APIField("phone", writable=True), APIField("email", writable=True), APIField("address", writable=True), APIField("map_embed_url", writable=True), APIField("working_hours", writable=True), APIField("is_active", writable=True)]

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Contact Info")
        verbose_name_plural = _("Contact Info")


class SocialLink(models.Model):
    platform = models.CharField(max_length=40, verbose_name=_("Platform"))
    url = models.URLField(verbose_name=_("URL"))
    icon = models.CharField(max_length=30, blank=True, verbose_name=_("Icon"))
    sort_order = models.PositiveIntegerField(default=0, verbose_name=_("Sort order"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    panels = [FieldPanel("platform"), FieldPanel("url"), FieldPanel("icon"), FieldPanel("sort_order"), FieldPanel("is_active")]
    api_fields = [APIField("platform", writable=True), APIField("url", writable=True), APIField("icon", writable=True), APIField("sort_order", writable=True), APIField("is_active", writable=True)]

    def __str__(self):
        return self.platform

    class Meta:
        verbose_name = _("Social Link")
        verbose_name_plural = _("Social Links")
        ordering = ["sort_order", "platform"]


class PricingPlan(ClusterableModel):
    name = models.CharField(max_length=100, verbose_name=_("Plan name"))
    price = models.CharField(max_length=50, verbose_name=_("Price"))
    period = models.CharField(max_length=40, blank=True, default="monthly", verbose_name=_("Period"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    button_text = models.CharField(max_length=50, blank=True, default="Get started", verbose_name=_("Button text"))
    button_link = models.URLField(blank=True, verbose_name=_("Button link"))
    is_featured = models.BooleanField(default=False, verbose_name=_("Featured"))
    sort_order = models.PositiveIntegerField(default=0, verbose_name=_("Sort order"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    panels = [
        FieldPanel("name"), FieldPanel("price"), FieldPanel("period"), FieldPanel("description"),
        FieldPanel("button_text"), FieldPanel("button_link"), FieldPanel("is_featured"),
        FieldPanel("sort_order"), FieldPanel("is_active"),
        InlinePanel("features", label=_("Feature"), min_num=0),
    ]
    api_fields = [APIField("name", writable=True), APIField("price", writable=True), APIField("period", writable=True), APIField("description", writable=True), APIField("button_text", writable=True), APIField("button_link", writable=True), APIField("is_featured", writable=True), APIField("sort_order", writable=True), APIField("is_active", writable=True), APIField("features", writable=True)]

    def __str__(self):
        return f"{self.name} — {self.price}"

    class Meta:
        verbose_name = _("Pricing Plan")
        verbose_name_plural = _("Pricing Plans")
        ordering = ["sort_order", "name"]


class PricingFeature(Orderable):
    plan = ParentalKey("home.PricingPlan", on_delete=models.CASCADE, related_name="features")
    text = models.CharField(max_length=200, verbose_name=_("Feature text"))
    is_included = models.BooleanField(default=True, verbose_name=_("Included"))
    panels = [FieldPanel("text"), FieldPanel("is_included")]
    api_fields = [APIField("text", writable=True), APIField("is_included", writable=True)]


class Feature(models.Model):
    title = models.CharField(max_length=120, verbose_name=_("Title"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    icon = models.CharField(max_length=50, blank=True, default="✦", verbose_name=_("Icon"))
    image = models.ForeignKey("wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+", verbose_name=_("Image"))
    sort_order = models.PositiveIntegerField(default=0, verbose_name=_("Sort order"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    panels = [FieldPanel("title"), FieldPanel("description"), FieldPanel("icon"), FieldPanel("image"), FieldPanel("sort_order"), FieldPanel("is_active")]
    api_fields = [APIField("title", writable=True), APIField("description", writable=True), APIField("icon", writable=True), APIField("image", writable=True), APIField("sort_order", writable=True), APIField("is_active", writable=True)]

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Feature")
        verbose_name_plural = _("Features")
        ordering = ["sort_order", "title"]
