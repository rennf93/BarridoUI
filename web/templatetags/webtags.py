import re
from django import template
from django.conf import settings
from django.urls import reverse, NoReverseMatch

import web.views.models.applications
from web.lib import get_applications, has_access_to_app_element

register = template.Library()


@register.simple_tag(takes_context=True)
def active(context, pattern_or_urlname):
    try:
        pattern = '^' + reverse(pattern_or_urlname)
    except NoReverseMatch:
        pattern = pattern_or_urlname
    path = getattr(context.get("request"), "path")
    if re.search(pattern, path):
        return 'active'
    return ''


@register.simple_tag(takes_context=False)
def get_settings(varname):
    return getattr(settings, varname)


@register.simple_tag(takes_context=False)
def get_applications_template(request, force_reload):
    apps = get_applications(request, force_reload)
    available_apps = []
    for app in apps:
        if has_access_to_app_element('strategy_exec', app["code"], request.user):
            available_apps.append(app)
    return web.views.models.applications.build_applications_nav_template(available_apps, request.user)
