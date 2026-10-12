# Seed demo snippets and a StandardPage for testing

from django.db import migrations


def seed(apps, schema_editor):
    ContentType = apps.get_model("contenttypes", "ContentType")
    Page = apps.get_model("wagtailcore", "Page")
    StandardPage = apps.get_model("home", "StandardPage")
    Site = apps.get_model("wagtailcore", "Site")

    # ── Snippets ──────────────────────────────────────────
    Navbar = apps.get_model("home", "Navbar")
    NavbarMenuItem = apps.get_model("home", "NavbarMenuItem")
    Footer = apps.get_model("home", "Footer")
    FooterLink = apps.get_model("home", "FooterLink")
    FooterSocialLink = apps.get_model("home", "FooterSocialLink")
    AlertBar = apps.get_model("home", "AlertBar")
    CTABanner = apps.get_model("home", "CTABanner")
    HeroBanner = apps.get_model("home", "HeroBanner")
    Testimonial = apps.get_model("home", "Testimonial")
    TeamMember = apps.get_model("home", "TeamMember")
    Service = apps.get_model("home", "Service")
    FAQItem = apps.get_model("home", "FAQItem")
    Accordion = apps.get_model("home", "Accordion")
    AccordionPanel = apps.get_model("home", "AccordionPanel")
    PartnerLogo = apps.get_model("home", "PartnerLogo")
    ContactInfo = apps.get_model("home", "ContactInfo")
    SocialLink = apps.get_model("home", "SocialLink")
    PricingPlan = apps.get_model("home", "PricingPlan")
    PricingFeature = apps.get_model("home", "PricingFeature")
    Feature = apps.get_model("home", "Feature")

    if not Navbar.objects.filter(title="Demo Navbar").exists():
        nav = Navbar.objects.create(
            title="Demo Navbar",
            logo_text="Demo Site",
            cta_text="Contact us",
            cta_link="/demo-snippets/",
            is_active=True,
        )
        NavbarMenuItem.objects.create(navbar=nav, label="Home", link_url="/", sort_order=0)
        NavbarMenuItem.objects.create(navbar=nav, label="Demo", link_url="/demo-snippets/", sort_order=1)
        NavbarMenuItem.objects.create(navbar=nav, label="About", link_url="/#about", sort_order=2)

    if not Footer.objects.filter(title="Demo Footer").exists():
        foot = Footer.objects.create(
            title="Demo Footer",
            copyright_text="© 2026 Demo — Wagtail + Grok",
            about_text="This footer is a reusable Snippet.",
            is_active=True,
        )
        FooterLink.objects.create(footer=foot, label="Privacy", link_url="/privacy/", sort_order=0)
        FooterLink.objects.create(footer=foot, label="Demo page", link_url="/demo-snippets/", sort_order=1)
        FooterSocialLink.objects.create(footer=foot, platform="Instagram", url="https://instagram.com", icon="📷", sort_order=0)
        FooterSocialLink.objects.create(footer=foot, platform="LinkedIn", url="https://linkedin.com", icon="💼", sort_order=1)

    if not AlertBar.objects.filter(message__startswith="Demo alert").exists():
        AlertBar.objects.create(
            message="Demo alert: all sample snippets are ready in admin → Snippets",
            link_text="Open demo page",
            link_url="/demo-snippets/",
            style="promo",
            is_dismissible=True,
            is_active=True,
        )

    if not CTABanner.objects.filter(title="Ready to build?").exists():
        CTABanner.objects.create(
            title="Ready to build?",
            text="This CTA Banner is a reusable snippet you can drop anywhere.",
            button_text="Get started",
            button_link="/demo-snippets/",
            background_style="accent",
            is_active=True,
        )

    if not HeroBanner.objects.filter(title="Welcome to the demo").exists():
        HeroBanner.objects.create(
            title="Welcome to the demo",
            subtitle="<p>Hero Banner snippet — title, subtitle, optional image and button.</p>",
            button_text="Explore",
            button_link="/demo-snippets/",
            is_active=True,
        )

    if not Testimonial.objects.filter(name="Sara Ahmadi").exists():
        Testimonial.objects.create(
            name="Sara Ahmadi",
            role="CEO, Sample Co",
            quote="Wagtail snippets made our site consistent and easy to manage.",
            rating=5,
            is_featured=True,
        )
        Testimonial.objects.create(
            name="Ali Rezaei",
            role="Product Manager",
            quote="We reuse the same CTA and FAQ across multiple pages.",
            rating=5,
            is_featured=True,
        )

    if not TeamMember.objects.filter(name="Mina Karimi").exists():
        TeamMember.objects.create(
            name="Mina Karimi",
            role="Lead Designer",
            bio="Designs clean interfaces and brand systems.",
            email="mina@example.com",
            sort_order=0,
        )
        TeamMember.objects.create(
            name="Reza Nouri",
            role="Backend Developer",
            bio="Works on Wagtail, APIs and infrastructure.",
            email="reza@example.com",
            sort_order=1,
        )

    if not Service.objects.filter(title="Web Design").exists():
        Service.objects.create(
            title="Web Design",
            short_description="Modern, responsive websites.",
            full_description="<p>Full design and build with Wagtail CMS.</p>",
            icon="🎨",
            is_featured=True,
            sort_order=0,
        )
        Service.objects.create(
            title="SEO & Content",
            short_description="Structure content for search and clarity.",
            full_description="<p>Pages, snippets and on-page SEO.</p>",
            icon="🔍",
            is_featured=True,
            sort_order=1,
        )

    if not FAQItem.objects.filter(question="What is a Snippet?").exists():
        FAQItem.objects.create(
            question="What is a Snippet?",
            answer="<p>A reusable piece of content (menu, footer, testimonial, …) managed once and used in many places.</p>",
            category="Basics",
            sort_order=0,
            is_active=True,
        )
        FAQItem.objects.create(
            question="How do I edit snippets?",
            answer="<p>In the admin sidebar open <strong>Snippets</strong>, pick a type, then edit or create entries.</p>",
            category="Basics",
            sort_order=1,
            is_active=True,
        )

    if not Accordion.objects.filter(title="Demo Accordion").exists():
        acc = Accordion.objects.create(title="Demo Accordion", heading="How it works", is_active=True)
        AccordionPanel.objects.create(
            accordion=acc,
            title="Step 1 — Create snippet",
            content="<p>Add content under Snippets in the admin.</p>",
            is_open_by_default=True,
            sort_order=0,
        )
        AccordionPanel.objects.create(
            accordion=acc,
            title="Step 2 — Use on site",
            content="<p>Navbar/Footer/Alert show site-wide; others can be queried in templates or pages.</p>",
            is_open_by_default=False,
            sort_order=1,
        )

    if not PartnerLogo.objects.filter(name="Partner Alpha").exists():
        PartnerLogo.objects.create(name="Partner Alpha", website="https://example.com", sort_order=0, is_active=True)
        PartnerLogo.objects.create(name="Partner Beta", website="https://example.org", sort_order=1, is_active=True)

    if not ContactInfo.objects.filter(title="Main office").exists():
        ContactInfo.objects.create(
            title="Main office",
            phone="+98 21 0000 0000",
            email="hello@example.com",
            address="Tehran, Iran",
            working_hours="Sat–Thu 9:00–18:00",
            is_active=True,
        )

    if not SocialLink.objects.filter(platform="Telegram").exists():
        SocialLink.objects.create(platform="Telegram", url="https://t.me/example", icon="✈️", sort_order=0, is_active=True)
        SocialLink.objects.create(platform="X / Twitter", url="https://x.com/example", icon="𝕏", sort_order=1, is_active=True)

    if not PricingPlan.objects.filter(name="Starter").exists():
        starter = PricingPlan.objects.create(
            name="Starter",
            price="1,500,000 تومان",
            period="monthly",
            description="For small sites",
            button_text="Choose Starter",
            button_link="/demo-snippets/",
            is_featured=False,
            sort_order=0,
            is_active=True,
        )
        PricingFeature.objects.create(plan=starter, text="1 site", is_included=True, sort_order=0)
        PricingFeature.objects.create(plan=starter, text="Basic support", is_included=True, sort_order=1)

        pro = PricingPlan.objects.create(
            name="Pro",
            price="4,500,000 تومان",
            period="monthly",
            description="For growing teams",
            button_text="Choose Pro",
            button_link="/demo-snippets/",
            is_featured=True,
            sort_order=1,
            is_active=True,
        )
        PricingFeature.objects.create(plan=pro, text="Unlimited pages", is_included=True, sort_order=0)
        PricingFeature.objects.create(plan=pro, text="Priority support", is_included=True, sort_order=1)
        PricingFeature.objects.create(plan=pro, text="Custom snippets", is_included=True, sort_order=2)

    if not Feature.objects.filter(title="Reusable content").exists():
        Feature.objects.create(
            title="Reusable content",
            description="Edit once, use everywhere.",
            icon="♻️",
            sort_order=0,
            is_active=True,
        )
        Feature.objects.create(
            title="MCP ready",
            description="Create and update snippets via API / MCP.",
            icon="🤖",
            sort_order=1,
            is_active=True,
        )

    # ── Demo StandardPage ─────────────────────────────────
    if StandardPage.objects.filter(slug="demo-snippets").exists():
        return

    try:
        home = Page.objects.get(slug="home", depth=2)
    except Page.DoesNotExist:
        home = Page.objects.filter(depth=2).first()
    if home is None:
        return

    ct = ContentType.objects.get_for_model(StandardPage)
    intro = (
        "<p>This page is a <strong>demo</strong> for Snippets. "
        "Open <strong>Admin → Snippets</strong> to see all types.</p>"
        "<ul>"
        "<li><strong>Site-wide:</strong> Navbar, Footer, Alert Bar (see header/footer of this site)</li>"
        "<li><strong>Banners:</strong> CTA Banner, Hero Banner</li>"
        "<li><strong>Content:</strong> Testimonial, FAQ, Accordion, Feature</li>"
        "<li><strong>Business:</strong> Service, Pricing Plan, Team, Partners, Contact, Social</li>"
        "</ul>"
        "<p>Sample records were created automatically (names like Demo Navbar, Sara Ahmadi, Starter plan).</p>"
    )
    body = []  # empty StreamField JSON

    page = StandardPage(
        title="Demo Snippets",
        slug="demo-snippets",
        intro=intro,
        body=body,
        content_type=ct,
        locale_id=home.locale_id,
        live=True,
        has_unpublished_changes=False,
        first_published_at=home.first_published_at,
    )
    home.add_child(instance=page)
    page.save_revision().publish()


def unseed(apps, schema_editor):
    StandardPage = apps.get_model("home", "StandardPage")
    StandardPage.objects.filter(slug="demo-snippets").delete()


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0008_herobanner_contactinfo_sociallink_pricingplan_feature"),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
