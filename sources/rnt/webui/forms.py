from django import forms
from django.db.models.query_utils import Q
from django.forms.widgets import HiddenInput
from django.utils.html import format_html
from django.utils.translation import ugettext as _

from mediane.distances import enumeration as enum_dist
from mediane.models import DataSet, Algorithm, Distance, Normalization
from mediane.normalizations import enumeration as enum_norm
from mediane.process import evaluate_dataset_and_provide_stats


class DataSetModelForm(forms.ModelForm):
    class Meta:
        model = DataSet
        fields = [
            'name',
            'content',
            'step',
            'public',
            # 'transient',
            # 'n',
            # 'm',
            # 'complete',
        ]
        # read_only_fields = [
        #     'n',
        #     'm',
        #     'complete',
        # ]
        help_texts = {
            'content': _('dataset_format_help_text'),
            # 'requirements':' '
        }
        labels = {
            "content": _("DataSet"),
        }

    def __init__(self, *args, **kwargs):
        super(DataSetModelForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        # if instance and instance.pk:
        #     for field_name in self.Meta.read_only_fields:
        #         self.fields[field_name].widget.attrs['readonly'] = True

    def clean(self):
        self.evaluation = evaluate_dataset_and_provide_stats(self.cleaned_data["content"].split("\n"))

        for line, msg in self.evaluation["invalid_rankings_id"].items():
            self.add_error('content', _("At line %(line)d: %(msg)s") % dict(line=line, msg=msg))

            # self.cleaned_data["n"] = self.evaluation["n"]
            # self.cleaned_data["m"] = self.evaluation["m"]
            # self.cleaned_data["complete"] = self.evaluation["complete"]
            # print(self.transient)

    def save(self, commit=True):
        instance = super(DataSetModelForm, self).save(commit=False)
        instance.n = self.evaluation["n"]
        instance.m = self.evaluation["m"]
        instance.complete = self.evaluation["complete"]

        if commit:
            instance.save()
        return instance


class ComputeConsensusForm(forms.Form):
    dataset = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'rows': '8'}),
        help_text=format_html(_('dataset_format_help_text')),
        initial="""r1 := [[A, C],[B, D],[E]]
r2 := [[A],[D],[B,E],[C]]
r3 := [[B,D],[C],[A],[E]]
r4 := [[B],[C],[A,D,E]]""",
    )
    dbdatasets = forms.ModelMultipleChoiceField(
        queryset=DataSet.objects.all(),
        required=False,
    )
    norm = forms.ChoiceField(
        choices=enum_norm.as_tuple_list(),
        widget=forms.RadioSelect,
        label='',
    )
    dist = forms.ModelChoiceField(
        queryset=Distance.objects.filter(~Q(pk__isnull=True)),
        widget=forms.RadioSelect,
        label='',
        empty_label=None,
    )
    algo = forms.MultipleChoiceField(
        choices=[],
        widget=forms.CheckboxSelectMultiple,
        label='',
    )
    norm_auto = forms.BooleanField(
        initial=True,
        required=False,
    )
    dist_auto = forms.BooleanField(
        initial=True,
        required=False,
    )
    algo_auto = forms.BooleanField(
        initial=True,
        required=False,
    )
    bench = forms.BooleanField(
        initial=False,
        label=_('bench'),
        required=False,
    )
    auto_compute = forms.BooleanField(
        initial=False,
        label=_('auto_compute_label'),
        help_text=_('auto_compute_help_text'),
        required=False,
    )
    extended_analysis = forms.BooleanField(
        initial=False,
        label=_('extended_analysis_label'),
        help_text=_('extended_analysis_help_text'),
        required=False,
    )
    ranking_source = forms.CharField(
        required=True,
        widget=HiddenInput
    )

    def __init__(self, user, *args, **kwargs):
        super(ComputeConsensusForm, self).__init__(*args, **kwargs)
        # self.fields['dbdatasets'].queryset = DataSet.objects.filter(Q(owner=request.user) | Q(public=True))
        if user.is_superuser:
            q = ~Q(pk=None)
        else:
            q = Q(public=True)
        self.fields['algo'].choices = [
            (k, _(k)) for k in
            Algorithm.objects.filter(q).values_list('key_name', flat=True)
            ]
        self.fields['dist'].queryset = Distance.objects.filter(q).order_by("id_order")
        self.fields['norm'].choices = [
            (k, _(k)) for k in
            Normalization.objects.filter(q).values_list('key_name', flat=True)
            ]

    def clean(self):
        cleaned_data = super(ComputeConsensusForm, self).clean()
        self.evaluation = evaluate_dataset_and_provide_stats(cleaned_data.get("dataset").split("\n"))
        self.cleaned_data["rankings"] = self.evaluation["rankings"]

        if self.evaluation["invalid"]:
            for line, msg in self.evaluation["invalid_rankings_id"].items():
                self.add_error('dataset', "At line %d: %s" % (line, msg))
