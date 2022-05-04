from django import forms
from .models import Token
import datetime
import string
import random
from dateutil.relativedelta import relativedelta

def get_token(length:int)->str:
    # choose from all lowercase letter
    characters = string.ascii_letters + string.digits + string.punctuation
    return u"".join(random.choice(characters) for i in range(length))


class DateInput(forms.DateInput):
    input_type = 'date'


class DateSelection(forms.Form):
    starting_date = forms.DateTimeField(widget=DateInput(attrs={'class':'input'}), label='Date de début ', required=True)
    ending_date = forms.DateTimeField(widget=DateInput(attrs={'class':'input'}), label='Date de fin ', required=True)

    def __init__(self, *args, **kwargs):
        super(DateSelection, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

class TokenForm(forms.ModelForm):
    EXPIRATION = [
        ('M1', '1 mois'),
        ('M3', '3 mois'),
        ('M6', '6 mois'),
        ('A1', '12 mois'),
        ('N0', 'N\'expire pas'),
    ]

    name = forms.CharField(max_length=255,label='Nom du token')
    expire = forms.CharField(label='Date d\'expiration',max_length=2,widget=forms.Select(choices=EXPIRATION))

    class Meta:
        model = Token
        fields = ('name','expire')

    def save(self,user):
        token = super(TokenForm, self).save(commit=False)
        current_date = datetime.datetime.now()
        expire_date = None
        if self.cleaned_data['expire'] == 'M1':
            expire_date = current_date + relativedelta(months=1)
        elif self.cleaned_data['expire'] == 'M3':
            expire_date = current_date + relativedelta(months=3)
        elif self.cleaned_data['expire'] == 'M6':
            expire_date = current_date + relativedelta(months=6)
        elif self.cleaned_data['expire'] == 'A1':
            expire_date = current_date + relativedelta(years=1)

        token.expire_at = expire_date
        tk = get_token(20)
        token.hash = tk
        token.user = user

        token.save()
        return tk
