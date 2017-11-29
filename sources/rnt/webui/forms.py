from django import forms
from django.utils.translation import ugettext as _

from mediane.algorithms import enumeration as enum_algo
from mediane.distances import enumeration as enum_dist
from mediane.normalizations import enumeration as enum_norm
from webui.models import DataSet


class TypeDatasetModelForm(forms.ModelForm):
    class Meta:
        model = DataSet
        exclude = [
            'transient',
        ]
        fields = [
            'content',
            'm',
            'n',
        ]
        help_texts = {
            'content': _("""Format
One ranking per line
A ranking should have the structure X := LIST (X is the name of the ranking)
A list should have the structure [BUCKET, ..., BUCKET]
A bucket should have the structure [element, ..., element] (the elements of the bucket should not contain [, ] and ,)"""),
            # 'requirements':' '
        }
        labels = {
            "content": _("Dataset"),
        }


class ComputeConsensusForm(forms.Form):
    dataset = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'rows': '8'}),
        help_text=_("""Format
One ranking per line
A ranking should have the structure X := LIST (X is the name of the ranking)
A list should have the structure [BUCKET, ..., BUCKET]
A bucket should have the structure [element, ..., element] (the elements of the bucket should not contain [, ] and ,)"""),
        initial="""r1 := [[A, C],[B, D],[E]]
r2 := [[A],[D],[B,E],[C]]
r3 := [[B,D],[C],[A],[E]]
r4 := [[B],[C],[A,D,E]]""",
    )
    norm = forms.ChoiceField(
        choices=enum_norm.as_tuple_list(),
        widget=forms.RadioSelect,
        label='',
    )
    dist = forms.ChoiceField(
        choices=enum_dist.as_tuple_list(),
        widget=forms.RadioSelect,
        label='',
    )
    algo = forms.ChoiceField(
        choices=enum_algo.as_tuple_list(),
        widget=forms.RadioSelect,
        label='',
    )
    norm_auto = forms.BooleanField(
        initial=True,
    )
    dist_auto = forms.BooleanField(
        initial=True,
    )
    algo_auto = forms.BooleanField(
        initial=True,
    )
