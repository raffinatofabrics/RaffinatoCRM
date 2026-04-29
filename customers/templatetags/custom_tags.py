from django import template
from customers.models import SystemSetting

register = template.Library()

@register.simple_tag
def get_logo_url():
    try:
        setting = SystemSetting.objects.first()
        if setting and setting.logo:
            return setting.logo.url
    except:
        pass
    return ''

@register.simple_tag
def get_company_name():
    try:
        setting = SystemSetting.objects.first()
        if setting:
            return setting.company_name
    except:
        pass
    return 'Raffinato'

@register.simple_tag
def get_subtitle():
    try:
        setting = SystemSetting.objects.first()
        if setting:
            return setting.subtitle
    except:
        pass
    return '面料外贸 CRM'