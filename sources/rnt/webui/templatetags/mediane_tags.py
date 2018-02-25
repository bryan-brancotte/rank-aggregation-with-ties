from django import template
from django.utils.safestring import mark_safe

register = template.Library()


def before_or_equals_cost_as_table(tab, elementsInR1):
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
<td rowspan="6">%s</td>
<td>A before B</td>
<td>%s</td>
</tr>
<tr>
<td>A after B</td>
<td>%s</td>
</tr>
<tr>
<td>A tied to B</td>
<td>%s</td>
</tr>
<tr>
<td>B is missing</td>
<td>%s</td>
</tr>
<tr>
<td>A is missing</td>
<td>%s</td>
</tr>
<tr>
<td>Both are missing</td>
<td>%s</td>
</tr>
</tbody>
</table>
""" % (
            elementsInR1,
            tab[0],
            tab[1],
            tab[2],
            tab[3],
            tab[4],
            tab[5],
        )
    )


@register.filter
def before_cost_as_table(val):
    return before_or_equals_cost_as_table(val[0], "A is before B")


@register.filter
def equal_cost_as_table(val):
    return before_or_equals_cost_as_table(val[1 ], "A is tied to B")
