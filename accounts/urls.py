"""Defines URL patterns for accounts."""

"""We import the path function, and then import the include function so we can include 
some default authentication URLs that Django has defined. These default URLs include 
named URL patterns, such as 'login' and 'logout'. We set the variable app_name to 
'accounts' so Django can distinguish these URLs from URLs belonging to other apps.
Even default URLs provided by Django, when included in the accounts app's urls.py file, 
will be accessible through the accounts namespace.

The login page's pattern matches the URL http://localhost:8000/accounts/login/. 
When Django reads this URL, the word accounts tells Django to look in accounts/urls.py, 
and login tells it to send requests to Django's default login view."""


from django.urls import path, include
from . import views

app_name = 'accounts'
urlpatterns = [
    # Include default auth urls.
    path('', include('django.contrib.auth.urls')),
    # Registration page.
    # The pattern for the registration page matches the URL http://localhost:8000/accounts/register/
    # and sends requests to the register() function in views
    path('register/', views.register, name='register'),
]
