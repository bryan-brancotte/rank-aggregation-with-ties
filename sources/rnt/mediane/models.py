from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _, ugettext
from django_pandas.managers import DataFrameManager
from rest_framework.compat import MinLengthValidator

from mediane import tasks
from mediane.algorithms.enumeration import get_from as get_algo_from
from mediane.median_ranking_tools import parse_ranking_with_ties_of_str
from mediane.process import execute_median_rankings_computation_of_result
from mediane.validators import sound_dataset_validator

import json
import random
import string


class DataSet(models.Model):
    name = models.CharField(
        max_length=64,
        unique=True,
        default="",
    )
    content = models.TextField(
        validators=[sound_dataset_validator, ],
    )
    m = models.IntegerField(
        help_text=_('The number of rankings'),
        default=0,
    )
    n = models.IntegerField(
        help_text=_('The number of elements'),
        default=0,
    )
    complete = models.BooleanField(
        help_text=_('Is each element present in each ranking of the dataset?'),
    )
    step = models.IntegerField(
        help_text=_('The number of steps used to generate the dataset, if pertinent'),
        blank=True,
        null=True,
    )
    transient = models.BooleanField(
        help_text=_('Should the dataset be deleted when the associated job is removed?'),
        default=False,
    )
    owner = models.ForeignKey(
        get_user_model(),
        help_text=_('The user who can see, edit and delete it'),
    )
    public = models.BooleanField(
        help_text=_('Can the dataset appear in the public database?'),
        default=False,
    )
    objects = DataFrameManager()

    def get_absolute_url(self):
        return reverse('webui:dataset-detail', args=[self.pk])

    @property
    def rankings(self):
        rankings = []
        for ranking_str in self.content.split('\n'):
            rankings.append(parse_ranking_with_ties_of_str(ranking_str))
        return rankings

    def __str__(self):
        spec = ["n=%i" % self.n, "m=%i" % self.m]
        if self.step is not None:
            spec.append("%s=%i" % (_('step'), self.step))
        spec = ', '.join(spec)
        if self.name != "":
            return "%s (%s)" % (self.name, spec)
        return spec

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        evaluation = sound_dataset_validator(self.content)
        self.n = evaluation['n']
        self.m = evaluation['m']
        self.complete = evaluation['complete']
        super(DataSet, self).save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,

        )


class Distance(models.Model):
    key_name = models.CharField(
        max_length=32,
        unique=True,
    )
    key_name_is_read_only = models.BooleanField(
        default=False,
    )
    owner = models.ForeignKey(
        get_user_model(),
        help_text=_('The user who can see, edit and delete it'),
    )
    public = models.BooleanField(
        help_text=_('Can it be seen by everyone?'),
        default=False,
    )
    scoring_scheme_str = models.TextField(
        verbose_name=_('scoring_scheme'),
        help_text=_('The scoring scheme in a json compatible format'),
        null=True,
        blank=True,
    )
    is_scoring_scheme_relevant = models.BooleanField(
        verbose_name=_('is_scoring_scheme_relevant'),
        help_text=_('Doas looking at the scoring scheme have a meaning ?'),
        default=False,
    )
    id_order = models.IntegerField(
        default=0
    )

    def __str__(self):
        return self.name

    @property
    def name(self):
        return ugettext(self.key_name + "_name")

    @property
    def desc(self):
        return ugettext(self.key_name + "_desc")

    @property
    def scoring_scheme(self):
        if self.scoring_scheme_str is None or self.scoring_scheme_str == "":
            return {}
        return json.loads(self.scoring_scheme_str)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        # try to parse the scoring scheme, causing an exception and making impossible to save invalid schema
        if self.is_scoring_scheme_relevant:
            self.scoring_scheme
        super(Distance, self).save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )


class Normalization(models.Model):
    key_name = models.CharField(
        max_length=32,
        unique=True,
    )
    key_name_is_read_only = models.BooleanField(
        default=False,
    )
    public = models.BooleanField(
        help_text=_('Can it be seen by everyone?'),
        default=False,
    )
    id_order = models.IntegerField(
        default=0
    )

    def __str__(self):
        return self.name

    @property
    def name(self):
        return ugettext(self.key_name + "_name")

    @property
    def desc(self):
        return ugettext(self.key_name + "_desc")


class Algorithm(models.Model):
    key_name = models.CharField(
        max_length=32,
        unique=True,
    )
    key_name_is_read_only = models.BooleanField(
        default=False,
    )
    public = models.BooleanField(
        help_text=_('Can it be seen by everyone?'),
        default=False,
    )
    id_order = models.IntegerField(
        default=0
    )
    objects = DataFrameManager()

    def __str__(self):
        return self.name

    @property
    def name(self):
        return ugettext(self.key_name)

    @property
    def desc(self):
        return ugettext(self.key_name + "_desc")

    def get_instance(self):
        return get_algo_from(self.key_name)()


class Job(models.Model):
    owner = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        help_text=_('User who created this job'),
    )
    dist = models.ForeignKey(
        Distance,
        on_delete=models.CASCADE,
        help_text=_('The distance used for this job'),
    )
    norm = models.ForeignKey(
        Normalization,
        on_delete=models.CASCADE,
        help_text=_('The distance used for this job'),
    )
    creation = models.DateTimeField(
        help_text=_('Creation time'),
    )
    bench = models.BooleanField(
        default=False,
        verbose_name=_('bench'),
    )
    identifier = models.CharField(
        max_length=32,
        validators=[MinLengthValidator(32), ],
    )
    task_count = models.IntegerField(
        verbose_name=_('task_count'),
        help_text=_('Number of results associated to it'),
        default=0,
    )
    status = models.IntegerField(choices=(
        (1, _("Pending")),
        (2, _("Running")),
        (4, _("Done")),
        (5, _("Error")),
        (6, _("Canceled"))
    ),
        default=1)
    name = models.CharField(
        max_length=256,
        null=True,
        blank=True,
    )

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        # create the identifier
        while self.identifier is None:
            self.identifier = ''.join(random.choice(''.join((string.ascii_letters, string.digits))) for _ in range(32))
            if Job.objects.filter(identifier=self.identifier):
                self.identifier = None

        # if status changed, update related tasks
        compute_on_this_thread = False
        if self.pk and self.status != Job.objects.get(pk=self.pk).status:
            if self.status == 1:
                for r in self.result_set.filter(distance_value__isnull=True):
                    r.mark_as_todo()
            elif self.status == 2:
                compute_on_this_thread = True
            elif self.status == 6:
                for r in self.result_set.all():
                    r.resultstoproducedecorator_set.all().delete()

        tasks_to_do = None
        if compute_on_this_thread:
            tasks_to_do = ResultsToProduceDecorator.objects.filter(result__job__pk=self.pk)
            if tasks_to_do.count() == 0:
                self.status = 4

        super(Job, self).save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )

        if compute_on_this_thread and self.status == 2:
            for r in tasks_to_do.only('pk'):
                tasks.compute_result(r.pk)

    def update_task_count(self):
        self.task_count = self.result_set.count()
        self.save()

    def get_name(self):
        return self.name or self.identifier

    def update_status(self, save=True):
        if self.status != 1 and self.status != 2:
            return
        has_error = False
        for r in self.result_set.all():
            if r.resultstoproducedecorator_set.filter(~Q(status=5)).count() > 0:
                return
            has_error = has_error or r.resultstoproducedecorator_set.filter(status=5).count() > 0
        if has_error:
            self.status = 5
        self.status = 4
        if save:
            self.save()

    def get_absolute_url(self):
        return reverse('webui:job-detail', args=[self.identifier])

    def __str__(self):
        return self.identifier


class Result(models.Model):
    algo = models.ForeignKey(
        Algorithm,
        on_delete=models.CASCADE,
        help_text=_('The distance used for this job'),
    )
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
    duration = models.FloatField(
        help_text=_('the duration expressed in ms'),
        blank=True,
        null=True,
    )
    consensuses = models.TextField(
        help_text=_('the consensus(es) computed for the given dataset and job\'s distance'),
        blank=True,
        null=True,
    )
    objects = DataFrameManager()

    def __str__(self):
        return "R%i: %s, %s, %s" % (self.pk, str(self.algo), str(self.dataset), str(self.job))

    def mark_as_todo(self):
        ResultsToProduceDecorator.objects.update_or_create(
            result=self,
            defaults=dict(
                status=1,
            ),
        )

    def compute(self):
        execute_median_rankings_computation_of_result(self)


class ResultsToProduceDecorator(models.Model):
    result = models.ForeignKey(
        Result,
        on_delete=models.CASCADE,
        help_text=_('The result to produce'),
    )
    status = models.IntegerField(choices=(
        (1, _("Pending")),
        (2, _("Taken for computation")),
        (3, _("Being computed")),
        (4, _("Done")),
        (5, _("Error"))
    ),
        default=1)

    @staticmethod
    def get_a_task():
        return ResultsToProduceDecorator.objects.filter(status=1).order_by('?').first()
