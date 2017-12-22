from django import template
from django.urls.base import reverse
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def as_p(value):
    output = []
    for s in value.split('\n'):
        if len(s) > 0:
            output.append('<p>%s</p>' % s)
    return mark_safe("".join(output))


@register.filter
def count_char(val, c='\n'):
    return val.count(c)


@register.filter
def count_line(val):
    return count_char(val, '\n') + 1


@register.filter
def max(i, cap):
    return i if i < cap else cap


@register.filter
def is_active_or_desc(request, pattern):
    try:
        if str(request.path).startswith(str(reverse(pattern))) \
                or str(request.path).startswith(str(pattern)):
            return 'active '
    except Exception:
        pass
    return ''


@register.filter
def is_active(request, pattern):
    try:
        if str(reverse(pattern)) == str(request.path) \
                or str(pattern) == str(request.path):
            return 'active '
    except Exception:
        pass
    return ''
