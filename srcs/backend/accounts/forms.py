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
            'class': 'form-input'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'PASSWORD',
            'class': 'form-input'
        })
    )

class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'USERNAME',
            'class': 'form-input'
        })
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'PASSWORD',
            'class': 'form-input'
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'REPEAT PASSWORD',
            'class': 'form-input'
        })
    )