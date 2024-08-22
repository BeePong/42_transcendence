from django.urls import path, include
from . import views

app_name = 'tournament'
urlpatterns = [
    path('', views.tournament, name='tournament'),
    path('create/', views.create_tournament, name='create_tournament'),
    path('solo_game/', views.solo_game, name='solo_game'),
    path('<int:tournament_id>/lobby/', views.tournament_lobby, name='tournament_lobby'),
    path('pong/', views.pong, name='pong'),
]
