from django.apps import AppConfig
from django.contrib.auth import get_user_model


class MedianeConfig(AppConfig):
    name = 'mediane'

    def ready(self):
        from mediane import distances, algorithms, normalizations
        from mediane.models import Distance, Algorithm, Normalization
        self.create_instances(distances.enumeration.as_tuple_list(), Distance, has_owner=True)
        self.create_instances(algorithms.enumeration.as_tuple_list(), Algorithm)
        self.create_instances(normalizations.enumeration.as_tuple_list(), Normalization)
        self.update_ordering(Distance)
        self.update_ordering(Normalization)
        self.update_ordering(Algorithm)

    def create_instances(self, tuple_list, klass, has_owner=False):
        try:
            defaults = dict(
                key_name_is_read_only=True,
            )
            if has_owner:
                defaults["owner"] = get_user_model().objects.get(id=1)
            for k, v in tuple_list:
                obj, created = klass.objects.update_or_create(
                    key_name=k,
                    defaults=defaults,
                )
                if created:
                    obj.public = False
        except Exception as e:
            print(e)
            pass


    def update_ordering(self, klass):
        try:
            elements = []
            for o in klass.objects.all():
                elements.append(o)
            elements = sorted(elements, key=lambda o: o.name)
            i = 0
            for o in elements:
                if o.id_order != i:
                    o.id_order = i
                    o.save()
                i += 1
        except Exception as e:
            print(e)
            pass
