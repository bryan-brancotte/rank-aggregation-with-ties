from django import template
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
