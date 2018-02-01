from mediane.admin.dist_norm_algo import DistNormAlgoAdmin


class DistanceAdmin(DistNormAlgoAdmin):
    list_display = ('key_name', 'name', 'desc', 'public', 'is_scoring_scheme_relevant')
    list_filter = ('public', 'is_scoring_scheme_relevant',)
