from bootstrapform.templatetags.bootstrap import bootstrap, bootstrap_inline
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


def before_or_equals_cost_as_table(tab, elementsInR1, prefix):
    return mark_safe(
        """
<table class="table">
<tbody>
<tr>
<td>consensus</td>
<td>Ranking r</td>
<td>cost</td>
</tr>
<tr>
<td rowspan="6">{0}</td>
<td>A before B</td>
<td id="{1}-0">{2}</td>
</tr>
<tr>
<td>A after B</td>
<td id="{1}-1">{3}</td>
</tr>
<tr>
<td>A tied to B</td>
<td id="{1}-2">{4}</td>
</tr>
<tr>
<td>B is missing</td>
<td id="{1}-3">{5}</td>
</tr>
<tr>
<td>A is missing</td>
<td id="{1}-4">{6}</td>
</tr>
<tr>
<td>Both are missing</td>
<td id="{1}-5">{7}</td>
</tr>
</tbody>
</table>
""".format(
            elementsInR1,
            prefix,
            tab[0],
            tab[1],
            tab[2],
            tab[3],
            tab[4],
            tab[5],
        )
    )


@register.filter
def before_cost_as_table_from_form(form):
    fields = [bootstrap_inline(f) for f in form if f.name.startswith("id_before_")]
    return before_cost_as_table([fields, ])


@register.filter
def before_cost_as_table(val):
    return before_or_equals_cost_as_table(val[0], "A is before B", "before")


@register.filter
def equal_cost_as_table_from_form(form):
    fields = [bootstrap_inline(f) for f in form if f.name.startswith("id_equal_")]
    return equal_cost_as_table([None, fields,])


@register.filter
def equal_cost_as_table(val):
    return before_or_equals_cost_as_table(val[1], "A is tied to B", "equal")
