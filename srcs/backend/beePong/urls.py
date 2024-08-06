from django.urls import path
from . import views

app_name = 'beePong'
urlpatterns = [
    path('api/', views.test, name='apiTest'),
    path('pong/', views.pong, name='pong'),
    path('navbar/', views.navbar, name='navbar'),
    path('home/', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('game/', views.game, name='game'),
    path('health/', views.health_check, name='health_check'),
]
