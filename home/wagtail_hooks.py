"""
All snippets under one sidebar parent: Snippets (classic icon).
Sub-items ordered by category so they appear as groups inside that menu.
Labels follow admin language (en / fa) via gettext_lazy.
"""
from django.utils.translation import gettext_lazy as _
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet, SnippetViewSetGroup

from home.snippet_models import (
    Accordion,
    AlertBar,
    ContactInfo,
    CTABanner,
    FAQItem,
    Feature,
    Footer,
    HeroBanner,
    Navbar,
    PartnerLogo,
    PricingPlan,
    Service,
    SocialLink,
    TeamMember,
    Testimonial,
)


# ── Site structure (order 100–199) ─────────────────────────

class NavbarViewSet(SnippetViewSet):
    model = Navbar
    icon = "list-ul"
    menu_label = _("Navbar")
    menu_order = 100


class FooterViewSet(SnippetViewSet):
    model = Footer
    icon = "resubmit"
    menu_label = _("Footer")
    menu_order = 110


class AlertBarViewSet(SnippetViewSet):
    model = AlertBar
    icon = "warning"
    menu_label = _("Alert Bar")
    menu_order = 120


class ContactInfoViewSet(SnippetViewSet):
    model = ContactInfo
    icon = "mail"
    menu_label = _("Contact Info")
    menu_order = 130


# ── Banners & CTA (order 200–299) ──────────────────────────

class CTABannerViewSet(SnippetViewSet):
    model = CTABanner
    icon = "pick"
    menu_label = _("CTA Banner")
    menu_order = 200


class HeroBannerViewSet(SnippetViewSet):
    model = HeroBanner
    icon = "image"
    menu_label = _("Hero Banner")
    menu_order = 210


# ── Content (order 300–399) ────────────────────────────────

class TestimonialViewSet(SnippetViewSet):
    model = Testimonial
    icon = "openquote"
    menu_label = _("Testimonial")
    menu_order = 300


class FAQItemViewSet(SnippetViewSet):
    model = FAQItem
    icon = "help"
    menu_label = _("FAQ Item")
    menu_order = 310


class AccordionViewSet(SnippetViewSet):
    model = Accordion
    icon = "order"
    menu_label = _("Accordion")
    menu_order = 320


class FeatureViewSet(SnippetViewSet):
    model = Feature
    icon = "tick-inverse"
    menu_label = _("Feature")
    menu_order = 330


# ── Services & Pricing (order 400–499) ─────────────────────

class ServiceViewSet(SnippetViewSet):
    model = Service
    icon = "cogs"
    menu_label = _("Service")
    menu_order = 400


class PricingPlanViewSet(SnippetViewSet):
    model = PricingPlan
    icon = "tag"
    menu_label = _("Pricing Plan")
    menu_order = 410


# ── Team & Partners (order 500–599) ────────────────────────

class TeamMemberViewSet(SnippetViewSet):
    model = TeamMember
    icon = "user"
    menu_label = _("Team Member")
    menu_order = 500


class PartnerLogoViewSet(SnippetViewSet):
    model = PartnerLogo
    icon = "group"
    menu_label = _("Partner Logo")
    menu_order = 510


class SocialLinkViewSet(SnippetViewSet):
    model = SocialLink
    icon = "link"
    menu_label = _("Social Link")
    menu_order = 520


# ── Single parent menu: Snippets (classic icon) ────────────

class SnippetsGroup(SnippetViewSetGroup):
    """One sidebar entry 'Snippets' — all types nested under it."""

    menu_label = _("Snippets")
    menu_icon = "snippet"
    menu_name = "snippets"
    menu_order = 250
    items = (
        # Site structure
        NavbarViewSet,
        FooterViewSet,
        AlertBarViewSet,
        ContactInfoViewSet,
        # Banners & CTA
        CTABannerViewSet,
        HeroBannerViewSet,
        # Content
        TestimonialViewSet,
        FAQItemViewSet,
        AccordionViewSet,
        FeatureViewSet,
        # Services & Pricing
        ServiceViewSet,
        PricingPlanViewSet,
        # Team & Partners
        TeamMemberViewSet,
        PartnerLogoViewSet,
        SocialLinkViewSet,
    )


register_snippet(SnippetsGroup)
