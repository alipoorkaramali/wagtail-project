"""
گروه‌بندی اسنیپت‌ها در پنل ادمین Wagtail
دسته‌ها:
  ۱. ساختار سایت
  ۲. فراخوان و بنر
  ۳. محتوا
  ۴. خدمات و قیمت
  ۵. تیم و همکاران
"""

from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet, SnippetViewSetGroup

from home.models import (
    Navbar,
    Footer,
    AlertBar,
    ContactInfo,
    CTABanner,
    HeroBanner,
    Testimonial,
    FAQItem,
    Accordion,
    Feature,
    Service,
    PricingPlan,
    TeamMember,
    PartnerLogo,
    SocialLink,
)


# ── ساختار سایت ──────────────────────────────────────────

class NavbarViewSet(SnippetViewSet):
    model = Navbar
    icon = "list-ul"
    menu_label = "منوی بالا"
    menu_order = 100


class FooterViewSet(SnippetViewSet):
    model = Footer
    icon = "resubmit"
    menu_label = "فوتر"
    menu_order = 110


class AlertBarViewSet(SnippetViewSet):
    model = AlertBar
    icon = "warning"
    menu_label = "نوار اعلان"
    menu_order = 120


class ContactInfoViewSet(SnippetViewSet):
    model = ContactInfo
    icon = "mail"
    menu_label = "اطلاعات تماس"
    menu_order = 130


class SiteStructureGroup(SnippetViewSetGroup):
    menu_label = "ساختار سایت"
    menu_icon = "folder-open-inverse"
    menu_order = 200
    items = (NavbarViewSet, FooterViewSet, AlertBarViewSet, ContactInfoViewSet)


# ── فراخوان و بنر ────────────────────────────────────────

class CTABannerViewSet(SnippetViewSet):
    model = CTABanner
    icon = "pick"
    menu_label = "بنر فراخوان"
    menu_order = 100


class HeroBannerViewSet(SnippetViewSet):
    model = HeroBanner
    icon = "image"
    menu_label = "بنر هیرو"
    menu_order = 110


class CallToActionGroup(SnippetViewSetGroup):
    menu_label = "فراخوان و بنر"
    menu_icon = "plus-inverse"
    menu_order = 210
    items = (CTABannerViewSet, HeroBannerViewSet)


# ── محتوا ────────────────────────────────────────────────

class TestimonialViewSet(SnippetViewSet):
    model = Testimonial
    icon = "openquote"
    menu_label = "نظر مشتری"
    menu_order = 100


class FAQItemViewSet(SnippetViewSet):
    model = FAQItem
    icon = "help"
    menu_label = "سوال متداول"
    menu_order = 110


class AccordionViewSet(SnippetViewSet):
    model = Accordion
    icon = "order"
    menu_label = "آکاردئون"
    menu_order = 120


class FeatureViewSet(SnippetViewSet):
    model = Feature
    icon = "tick-inverse"
    menu_label = "ویژگی"
    menu_order = 130


class ContentGroup(SnippetViewSetGroup):
    menu_label = "محتوا"
    menu_icon = "doc-full"
    menu_order = 220
    items = (TestimonialViewSet, FAQItemViewSet, AccordionViewSet, FeatureViewSet)


# ── خدمات و قیمت ─────────────────────────────────────────

class ServiceViewSet(SnippetViewSet):
    model = Service
    icon = "cogs"
    menu_label = "سرویس"
    menu_order = 100


class PricingPlanViewSet(SnippetViewSet):
    model = PricingPlan
    icon = "tag"
    menu_label = "پلن قیمت"
    menu_order = 110


class ServicesPricingGroup(SnippetViewSetGroup):
    menu_label = "خدمات و قیمت"
    menu_icon = "snippet"
    menu_order = 230
    items = (ServiceViewSet, PricingPlanViewSet)


# ── تیم و همکاران ────────────────────────────────────────

class TeamMemberViewSet(SnippetViewSet):
    model = TeamMember
    icon = "user"
    menu_label = "عضو تیم"
    menu_order = 100


class PartnerLogoViewSet(SnippetViewSet):
    model = PartnerLogo
    icon = "group"
    menu_label = "لوگوی همکار"
    menu_order = 110


class SocialLinkViewSet(SnippetViewSet):
    model = SocialLink
    icon = "link"
    menu_label = "شبکه اجتماعی"
    menu_order = 120


class TeamPartnersGroup(SnippetViewSetGroup):
    menu_label = "تیم و همکاران"
    menu_icon = "group"
    menu_order = 240
    items = (TeamMemberViewSet, PartnerLogoViewSet, SocialLinkViewSet)


# ثبت گروه‌ها
register_snippet(SiteStructureGroup)
register_snippet(CallToActionGroup)
register_snippet(ContentGroup)
register_snippet(ServicesPricingGroup)
register_snippet(TeamPartnersGroup)
