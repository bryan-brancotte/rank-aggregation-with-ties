from django.forms.widgets import CheckboxSelectMultiple


class CheckboxSelectMultipleAsTable(CheckboxSelectMultiple):
    template_name = 'webui/forms/widgets/multiple_input_as_table.html'
