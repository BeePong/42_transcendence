from django.urls import path
from . import views

app_name = 'beePong'
urlpatterns = [
    path('api/', views.test, name='apiTest'),
    path('navbar/', views.navbar, name='navbar'),
    path('home/', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('game/', views.game, name='game'),
    path('tournament/', views.tournament, name='tournament'),
    path('tournament/create/', views.create_tournament, name='create_tournament'),
    path('alias/', views.alias, name='alias'),
]