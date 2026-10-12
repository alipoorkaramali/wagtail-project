from django import template
from home.models import Navbar, Footer, AlertBar

register = template.Library()


@register.simple_tag
def get_active_navbar():
    """Return the first active Navbar snippet, or None."""
    return Navbar.objects.filter(is_active=True).first()


@register.simple_tag
def get_active_footer():
    """Return the first active Footer snippet, or None."""
    return Footer.objects.filter(is_active=True).first()


@register.simple_tag
def get_active_alert():
    """Return the first active AlertBar snippet, or None."""
    return AlertBar.objects.filter(is_active=True).first()
