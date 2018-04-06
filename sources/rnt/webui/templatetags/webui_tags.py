from bootstrapform.templatetags.bootstrap import bootstrap
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
def count_line_plus_one(val):
    return count_line(val) + 1


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


@register.filter
def tags_to_bootstrap(tag):
    if tag == "error":
        return "danger"
    if tag == "":
        return "info"
    return tag


@register.filter
def get_value_from_dict(mydict, key):
    return mydict.get(key, None)


@register.filter
def get_field(form, name):
    for field in form:
        if field.name == name:
            return bootstrap(field)
    return ""


@register.filter
def can_be_edited_by(obj, user):
    # if user.is_superuser:
    #     return True
    try:
        return obj.owner.pk == user.pk
    except:
        pass
    return False
