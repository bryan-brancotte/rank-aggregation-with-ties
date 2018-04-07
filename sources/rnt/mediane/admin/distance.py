from mediane.admin.dist_norm_algo import DistNormAlgoAdmin


class DistanceAdmin(DistNormAlgoAdmin):
    list_display = ('key_name', 'in_db_name', 'in_db_desc', 'public', 'is_scoring_scheme_relevant')
    list_filter = ('public', 'is_scoring_scheme_relevant',)
