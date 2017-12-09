from django import forms
from django.utils.html import format_html
from django.utils.translation import ugettext as _

from mediane.algorithms import enumeration as enum_algo
from mediane.distances import enumeration as enum_dist
from mediane.normalizations import enumeration as enum_norm
from webui.models import DataSet
from webui.process import evaluate_dataset_and_provide_stats


class DataSetModelForm(forms.ModelForm):
    class Meta:
        model = DataSet
        fields = [
            'name',
            'content',
            'step',
            'transient',
        ]
        help_texts = {
            'content': _('dataset_format_help_text'),
            # 'requirements':' '
        }
        labels = {
            "content": _("DataSet"),
        }



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
        label=_('precise time measurement'),
        required=False,
    )

    def clean(self):
        cleaned_data = super(ComputeConsensusForm, self).clean()
        evaluation = evaluate_dataset_and_provide_stats(cleaned_data.get("dataset").split("\n"))
        self.cleaned_data["rankings"] = evaluation["rankings"]

        if evaluation["invalid"]:
            for line, msg in evaluation["invalid_rankings_id"].items():
                self.add_error('dataset', "At line %d: %s" % (line, msg))
