from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _, ugettext

from mediane.algorithms.enumeration import get_from as get_algo_from
from mediane.median_ranking_tools import parse_ranking_with_ties_of_str
from mediane.validators import sound_dataset_validator

import json


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
        help_text=_('Should the dataset be deleted when the associated job is removed?'),
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

    def get_absolute_url(self):
        return reverse('webui:dataset_view', args=[self.pk])

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

    def __str__(self):
        return self.name

    @property
    def name(self):
        return ugettext(self.key_name)

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

    def __str__(self):
        return self.key_name

    @property
    def name(self):
        return ugettext(self.key_name)

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

    def __str__(self):
        return self.key_name

    @property
    def name(self):
        return ugettext(self.key_name)

    @property
    def desc(self):
        return ugettext(self.key_name + "_desc")

    def get_instance(self):
        return get_algo_from(self.key_name)


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

    def get_task(self):
        pass
        #  task = self.task_set.order_by('?').first()

    # def get_absolute_url(self):
    #     return reverse('webui:job_view', args=[self.pk])


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
    results = models.TextField(
        help_text=_('the consensus(es) computed for the givent dataset and job\'s distance'),
        blank=True,
        null=True,
    )

    # def get_absolute_url(self):
    #     return reverse('webui:result_view', args=[self.pk])
