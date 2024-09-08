from django import forms
from .models import Tournament, Player


class TournamentForm(forms.ModelForm):
    num_players = forms.ChoiceField(
        choices=[(2, "2"), (4, "4")],
        widget=forms.RadioSelect(attrs={"class": "radio-input"}),
    )

    class Meta:
        model = Tournament
        fields = ["title", "description", "num_players"]
        widgets = {
            "title": forms.TextInput(
                attrs={"placeholder": "TITLE", "class": "form__input"}
            ),
            "description": forms.TextInput(
                attrs={"placeholder": "DESCRIPTION", "class": "form__input"}
            ),
        }


class AliasForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ["alias"]
        widgets = {
            "alias": forms.TextInput(
                attrs={"placeholder": "ALIAS", "class": "forminput"}
            ),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super(AliasForm, self).__init__(*args, **kwargs)
        if self.user.username:
            self.fields["alias"].initial = self.user.username

    def clean_alias(self):
        alias = self.cleaned_data["alias"]
        if Player.objects.filter(alias=alias).exclude(user=self.user).exists():
            raise forms.ValidationError(
                "This alias is already taken, please choose another one."
            )
        return alias
