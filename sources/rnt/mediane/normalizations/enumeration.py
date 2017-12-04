from django.utils.translation import ugettext_lazy as _

NONE = 0
UNIFICATION = 1
PROJECTION = 2

__tuple_list = ((UNIFICATION, _("Unification")), (PROJECTION, _("Projection")), (NONE, _("None")),)


def as_tuple_list():
    return __tuple_list


def get_from(id):
    for k, v in __tuple_list:
        if str(k) == str(id):
            return v
    return None
