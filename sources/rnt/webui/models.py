# Create your models here.
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import ugettext_lazy as _


class DataSet(models.Model):
    content = models.TextField(
    )
    m = models.IntegerField(
        help_text=_('The number of rankings'),
    )
    n = models.IntegerField(
        help_text=_('The number of elements'),
    )
    step = models.IntegerField(
        help_text=_('The number of steps used to generate the dataset, if pertinent'),
    )
    transient = models.BooleanField(
        help_text=_('Should be deleted when the associated job is removed'),
    )


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
