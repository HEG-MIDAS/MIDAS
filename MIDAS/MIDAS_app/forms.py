from django import forms

class DateInput(forms.DateInput):
    input_type = 'date'


class DateSelection(forms.Form):
    starting_date = forms.DateTimeField(widget=DateInput(attrs={'class':'input'}), label='Date de début ', required=True)
    ending_date = forms.DateTimeField(widget=DateInput(attrs={'class':'input'}), label='Date de fin ', required=True)

    def __init__(self, *args, **kwargs):
        super(DateSelection, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
