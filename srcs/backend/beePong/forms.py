from django import forms
from .models import Tournament

class TournamentForm(forms.ModelForm):
    class Meta:
        model = Tournament
        fields = ['title', 'description', 'num_players']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'TITLE'}),
            'description': forms.TextInput(attrs={'placeholder': 'DESCRIPTION'}),
            'num_players': forms.TextInput(attrs={'placeholder': 'Number of players'}),
        }