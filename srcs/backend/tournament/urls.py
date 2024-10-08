from django.urls import path, include
from . import views
from django.contrib import admin

app_name = "tournament"
urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.tournament, name="tournament"),
    path("create/", views.create_tournament, name="create_tournament"),
    path("create_solo_game/", views.create_solo_game, name="create_solo_game"),
    path("<int:tournament_id>/solo_game/", views.tournament_lobby, name="solo_game"),
    path("<int:tournament_id>/lobby/", views.tournament_lobby, name="tournament_lobby"),
    # path("<int:tournament_id>/game/", views.tournament_lobby, name="tournament_lobby"),
]
