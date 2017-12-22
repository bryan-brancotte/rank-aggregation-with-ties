from django.core.exceptions import PermissionDenied


def ownership_required(class_object, owner_field="owner"):
    def real_decorator(function):
        def wrapper(request, *args, **kwargs):
            obj = class_object.objects.get(pk=kwargs['pk'])
            if getattr(obj, owner_field) == request.user:
                return function(request, *args, **kwargs)
            else:
                raise PermissionDenied

        return wrapper

    return real_decorator
