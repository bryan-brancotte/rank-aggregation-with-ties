# Create your models here.
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _

from webui.process import evaluate_dataset_and_provide_stats


class DataSet(models.Model):
    name = models.CharField(
        max_length=64,
        unique=True,
        default="",
    )
    content = models.TextField(
    )
    m = models.IntegerField(
        help_text=_('The number of rankings'),
    )
    n = models.IntegerField(
        help_text=_('The number of elements'),
    )
    complete = models.BooleanField(
        help_text=_('Are every elements present in each rankings of the dataset'),
    )
    step = models.IntegerField(
        help_text=_('The number of steps used to generate the dataset, if pertinent'),
        blank=True,
        null=True,
    )
    transient = models.BooleanField(
        help_text=_('Should be deleted when the associated job is removed'),
    )

    def get_absolute_url(self):
        return reverse('rnt:dataset_view', args=[self.pk])

    def __str__(self):
        spec = []
        spec.append("n=%i" % self.n)
        spec.append("m=%i" % self.m)
        if self.step is not None:
            spec.append("%s=%i" % (_('step'), self.m))
        spec = ', '.join(spec)
        if self.name != "":
            return "%s (%s)" % (self.name, spec)
        return spec


class Distance(models.Model):
    name = models.CharField(
        max_length=64,
        unique=True,
    )
    desc = models.TextField(
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.name


class Job(models.Model):
    owner = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        help_text=_('User who created this job'),
    )
    distance_used = models.ForeignKey(
        Distance,
        on_delete=models.CASCADE,
        help_text=_('The distance used for this job'),
    )
    creation = models.DateTimeField(
        help_text=_('Creation time'),
    )

    # def get_absolute_url(self):
    #     return reverse('rnt:job_view', args=[self.pk])


class Result(models.Model):
    dataset = models.ForeignKey(
        DataSet,
        on_delete=models.CASCADE,
    )
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
    )
    distance_value = models.FloatField(
        blank=True,
        null=True,
    )
    results = models.TextField(
        help_text=_('the consensus(es) computed for the givent dataset and job\'s distance'),
        blank=True,
        null=True,
    )

    # def get_absolute_url(self):
    #     return reverse('rnt:result_view', args=[self.pk])
