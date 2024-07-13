"""Defines URL patterns for accounts."""

"""We import the path function, and then import the include function so we can include 
some default authentication URLs that Django has defined. These default URLs include 
named URL patterns, such as 'login' and 'logout'. We set the variable app_name to 
'accounts' so Django can distinguish these URLs from URLs belonging to other apps.
Even default URLs provided by Django, when included in the accounts app's urls.py file, 
will be accessible through the accounts namespace."""

from django.urls import path, include
from . import views

app_name = 'accounts'
urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.custom_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),
]
