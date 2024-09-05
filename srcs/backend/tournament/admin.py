from django.contrib import admin
from .models import Player, Tournament, Match, PlayerTournament


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = (
        "username",
        "alias",
        "has_active_tournament",
        "is_online",
        "current_tournament_id",
        "created_at",
    )
    search_fields = ("username", "alias")


@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "state",
        "player_count",
        "num_players",
        "is_final",
        "created_at",
    )
    search_fields = ("title",)
    list_filter = ("state", "is_final")

    def player_count(self, obj):
        return obj.players.count()

    player_count.short_description = "Number of Players in"


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = (
        "game_id",
        "tournament__id",
        "player1__username",
        "player2__username",
        "state",
        "created_at",
        "winner",
    )
    search_fields = ("tournament__title", "player1__username", "player2__username")
    list_filter = ("state",)

    def tournament__id(self, obj):
        return obj.tournament.tournament_id

    def player1__username(self, obj):
        return obj.player1.username

    def player2__username(self, obj):
        return obj.player2.username

    def winner(self, obj):
        return obj.winner.username

    tournament__id.short_description = "Tournament ID"
    player1__username.short_description = "Player 1"
    player2__username.short_description = "Player 2"
    winner.short_description = "Winner"
