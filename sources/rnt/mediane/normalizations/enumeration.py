from django.utils.translation import ugettext_lazy as _

UNIFICATION = 1
PROJECTION = 2


def as_tuple_list():
    return (
        (
            UNIFICATION,
            _("UNIFICATION")
        ),
        (
            PROJECTION,
            _("PROJECTION")
        ),
    )
