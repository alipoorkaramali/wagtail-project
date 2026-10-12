"""Snippet categories in Wagtail admin. Labels follow admin language (en/fa)."""
from django.utils.translation import gettext_lazy as _
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet, SnippetViewSetGroup

from home.snippet_models import (
    Navbar, Footer, AlertBar, ContactInfo,
    CTABanner, HeroBanner,
    Testimonial, FAQItem, Accordion, Feature,
    Service, PricingPlan,
    TeamMember, PartnerLogo, SocialLink,
)


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


class SiteStructureGroup(SnippetViewSetGroup):
    menu_label = _("Site structure")
    menu_icon = "folder-open-inverse"
    menu_order = 200
    items = (NavbarViewSet, FooterViewSet, AlertBarViewSet, ContactInfoViewSet)


class CTABannerViewSet(SnippetViewSet):
    model = CTABanner
    icon = "pick"
    menu_label = _("CTA Banner")
    menu_order = 100


class HeroBannerViewSet(SnippetViewSet):
    model = HeroBanner
    icon = "image"
    menu_label = _("Hero Banner")
    menu_order = 110


class CallToActionGroup(SnippetViewSetGroup):
    menu_label = _("Banners & CTA")
    menu_icon = "plus-inverse"
    menu_order = 210
    items = (CTABannerViewSet, HeroBannerViewSet)


class TestimonialViewSet(SnippetViewSet):
    model = Testimonial
    icon = "openquote"
    menu_label = _("Testimonial")
    menu_order = 100


class FAQItemViewSet(SnippetViewSet):
    model = FAQItem
    icon = "help"
    menu_label = _("FAQ Item")
    menu_order = 110


class AccordionViewSet(SnippetViewSet):
    model = Accordion
    icon = "order"
    menu_label = _("Accordion")
    menu_order = 120


class FeatureViewSet(SnippetViewSet):
    model = Feature
    icon = "tick-inverse"
    menu_label = _("Feature")
    menu_order = 130


class ContentGroup(SnippetViewSetGroup):
    menu_label = _("Content")
    menu_icon = "doc-full"
    menu_order = 220
    items = (TestimonialViewSet, FAQItemViewSet, AccordionViewSet, FeatureViewSet)


class ServiceViewSet(SnippetViewSet):
    model = Service
    icon = "cogs"
    menu_label = _("Service")
    menu_order = 100


class PricingPlanViewSet(SnippetViewSet):
    model = PricingPlan
    icon = "tag"
    menu_label = _("Pricing Plan")
    menu_order = 110


class ServicesPricingGroup(SnippetViewSetGroup):
    menu_label = _("Services & Pricing")
    menu_icon = "snippet"
    menu_order = 230
    items = (ServiceViewSet, PricingPlanViewSet)


class TeamMemberViewSet(SnippetViewSet):
    model = TeamMember
    icon = "user"
    menu_label = _("Team Member")
    menu_order = 100


class PartnerLogoViewSet(SnippetViewSet):
    model = PartnerLogo
    icon = "group"
    menu_label = _("Partner Logo")
    menu_order = 110


class SocialLinkViewSet(SnippetViewSet):
    model = SocialLink
    icon = "link"
    menu_label = _("Social Link")
    menu_order = 120


class TeamPartnersGroup(SnippetViewSetGroup):
    menu_label = _("Team & Partners")
    menu_icon = "group"
    menu_order = 240
    items = (TeamMemberViewSet, PartnerLogoViewSet, SocialLinkViewSet)


register_snippet(SiteStructureGroup)
register_snippet(CallToActionGroup)
register_snippet(ContentGroup)
register_snippet(ServicesPricingGroup)
register_snippet(TeamPartnersGroup)
