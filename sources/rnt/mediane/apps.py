from django.apps import AppConfig


class MedianeConfig(AppConfig):
    name = 'mediane'

    def ready(self):
        from mediane import distances, algorithms, normalizations
        from mediane.models import Distance, Algorithm, Normalization
        self.create_instances(distances.enumeration.as_tuple_list(), Distance)
        self.create_instances(algorithms.enumeration.as_tuple_list(), Algorithm)
        self.create_instances(normalizations.enumeration.as_tuple_list(), Normalization)

    def create_instances(self, tuple_list, klass):
        try:
            for k, v in tuple_list:
                obj, created = klass.objects.update_or_create(
                    key_name=k,
                    defaults=dict(
                        key_name_is_read_only=True,
                    ),
                )
                if created:
                    obj.public = False
        except Exception as e:
            print(e)
            pass
