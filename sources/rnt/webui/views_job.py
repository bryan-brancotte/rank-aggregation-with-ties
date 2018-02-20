from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.query_utils import Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.urls.base import reverse
from django.utils.decorators import method_decorator
from django.views.generic.edit import DeleteView
from django.views.generic.list import ListView

from mediane.models import Job
from webui import views_generic
from webui.decorators import ownership_required



class JobDetailView(views_generic.HybridDetailView):
    model = Job
    slug_field = 'identifier'
    slug_url_kwarg = 'identifier'
    template_name = "webui/job_detail.html"

    def dispatch(self, *args, **kwargs):
        obj = self.get_object()
        if self.request.user.id == obj.owner.id or self.request.user.is_superuser:
            return super(JobDetailView, self).dispatch(*args, **kwargs)
        return redirect('%s?next=%s' % (reverse('webui:login'), self.request.path))

    def get_data(self, context):
        print(context)
        return {}
