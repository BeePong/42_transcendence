"""
This module contains custom authentication and user creation forms that extend
Django's built-in AuthenticationForm and UserCreationForm. These custom forms 
add placeholders and custom CSS classes to the username and password fields.
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'USERNAME',
            'class': 'form__input',
            'autocomplete': 'new-username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'PASSWORD',
            'class': 'form__input',
            'autocomplete': 'current-password'
        })
    )

class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'USERNAME',
            'class': 'form__input',
            'autocomplete': 'new-username'
        })
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'PASSWORD',
            'class': 'form__input'
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'REPEAT PASSWORD',
            'class': 'form__input'
        })
    )