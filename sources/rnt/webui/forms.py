import itertools
import json

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UsernameField, UserChangeForm
from django.db.models.query_utils import Q
from django.forms import ModelForm
from django.forms.widgets import HiddenInput
from django.utils.html import format_html
from django.utils.translation import ugettext as _

from mediane.distances import enumeration as enum_dist
from mediane.models import DataSet, Algorithm, Distance, Normalization
from mediane.normalizations import enumeration as enum_norm
from mediane.process import evaluate_dataset_and_provide_stats, cleanup_dataset


class DataSetForUploadModelForm(forms.ModelForm):
    class Meta:
        model = DataSet
        fields = [
            'step',
            'public',
        ]


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
        self.cleaned_data["content"] = cleanup_dataset(self.cleaned_data.get("content"))
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
    norm = forms.ModelChoiceField(
        queryset=Normalization.objects.filter(~Q(pk__isnull=True)),
        widget=forms.RadioSelect,
        label='',
        empty_label=None,
    )
    dist = forms.ModelChoiceField(
        queryset=Distance.objects.filter(~Q(pk__isnull=True)),
        widget=forms.RadioSelect,
        label='',
        empty_label=None,
    )
    algo = forms.ModelMultipleChoiceField(
        queryset=None,
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
        self.fields['algo'].queryset = Algorithm.objects.filter(can_be_executed=True).filter(q).order_by("id_order")
        self.fields['dist'].queryset = Distance.objects.filter(q).order_by("id_order")
        self.fields['norm'].queryset = Normalization.objects.filter(q).order_by("id_order")

    def clean(self):
        cleaned_data = super(ComputeConsensusForm, self).clean()
        cleaned_data["dataset"] = cleanup_dataset(cleaned_data.get("dataset"))
        self.evaluation = evaluate_dataset_and_provide_stats(cleaned_data.get("dataset").split("\n"))
        self.cleaned_data["rankings"] = self.evaluation["rankings"]

        if self.evaluation["invalid"]:
            for line, msg in self.evaluation["invalid_rankings_id"].items():
                self.add_error('dataset', "At line %d: %s" % (line, msg))


class UserCreationFormWithMore(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ("username", "email", "first_name", "last_name")
        field_classes = {'username': UsernameField}

    def __init__(self, *args, **kwargs):
        super(UserCreationFormWithMore, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({'required': True})


class MyUserChangeForm(UserChangeForm):
    class Meta:
        model = get_user_model()
        fields = ("username", "email", "first_name", "last_name", "password")


class UserDeleteForm(ModelForm):
    class Meta:
        model = get_user_model()
        fields = ()


class DistanceModelForm(ModelForm):
    class Meta:
        model = Distance
        fields = [
            'key_name',
            'in_db_name',
            'in_db_desc',
            'public',
            'is_scoring_scheme_relevant',
        ]
        widgets = {
            'in_db_desc': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super(DistanceModelForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.key_name_is_read_only:
            self.fields['key_name'].disabled = True
            print(dir(self.fields['in_db_name']))
            print(instance.name)
            del self.fields['in_db_name']
            del self.fields['in_db_desc']
        if instance:
            scoring_scheme = instance.scoring_scheme
        else:
            scoring_scheme = Distance.objects.get(key_name="KTG").scoring_scheme

        for (prefix, i), coef in zip(
                itertools.product(["before", "equal"], range(0, 6)),
                itertools.chain(scoring_scheme[0], scoring_scheme[1])
        ):
            self.fields['id_{}_{}'.format(prefix, i)] = forms.CharField(
                initial=coef,
                widget=forms.NumberInput()
            )

    def clean(self):
        scoring_scheme = [[], []]
        for (prefix, pos), i in itertools.product([("before", 0), ("equal", 1)], range(0, 6)):
            scoring_scheme[pos].append(self.cleaned_data['id_{}_{}'.format(prefix, i)])
        self.scoring_scheme = scoring_scheme

    def save(self, commit=True):
        instance = super(DistanceModelForm, self).save(commit=False)
        instance.scoring_scheme_str = json.dumps(self.scoring_scheme)

        if commit:
            instance.save()
        return instance
