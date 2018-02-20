from django.utils.translation import ugettext_lazy as _

NONE = 'None'
UNIFICATION = 'UNIF'
PROJECTION = 'PROJ'

__tuple_list = ((UNIFICATION, _(UNIFICATION)), (PROJECTION, _(PROJECTION)), (NONE, _(NONE)),)


def as_tuple_list():
    return __tuple_list


def get_from(id_enum):
    for k, v in __tuple_list:
        if str(k) == str(id_enum):
            return v
    return None

def __dummy_method_to_have_translations():
    _('None_name')
    _('UNIF_name')
    _('PROJ_name')
    _('None_desc')
    _('UNIF_desc')
    _('PROJ_desc')