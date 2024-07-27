from django import forms
from .models import Tournament, Alias

class TournamentForm(forms.ModelForm):
    num_players = forms.ChoiceField(
        choices=[(2, '2'), (4, '4')],
        widget=forms.RadioSelect(attrs={'class': 'radio-input'})
    )

    class Meta:
        model = Tournament
        fields = ['title', 'description', 'num_players']
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'TITLE',
                'class': 'form-input'
            }),
            'description': forms.TextInput(attrs={
                'placeholder': 'DESCRIPTION',
                'class': 'form-input'
            })
        }

class AliasForm(forms.ModelForm):
    class Meta:
        model = Alias
        fields = ['alias']
        widgets = {
            'alias': forms.TextInput(attrs={
                'placeholder': 'ALIAS',
                'class': 'form-input'
            }),
        }

    def __init__(self, *args, **kwargs):
        username = kwargs.pop('username', None)
        super(AliasForm, self).__init__(*args, **kwargs)
        if username:
            self.fields['alias'].initial = username