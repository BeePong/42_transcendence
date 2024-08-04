from django.contrib import admin
from .models import Player, Game, Tournament, PlayerTournament

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('player_id', 'username', 'alias', 'is_registered', 'is_online', 'current_tournament_id', 'created_at')
    search_fields = ('username', 'alias')
    list_filter = ('is_registered', 'is_online')
    ordering = ('-created_at',)

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('game_id', 'player1', 'player1_score', 'player2', 'player2_score', 'state', 'winner', 'created_at')
    search_fields = ('state',)
    list_filter = ('state',)
    ordering = ('-created_at',)

@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ('tournament_id', 'name', 'state', 'num_players', 'winner', 'created_at')
    search_fields = ('name', 'state')
    list_filter = ('state',)
    ordering = ('-created_at',)

@admin.register(PlayerTournament)
class PlayerTournamentAdmin(admin.ModelAdmin):
    list_display = ('player_tournament_id', 'player', 'tournament', 'created_at')
    search_fields = ('player__username', 'tournament__name')
    list_filter = ('tournament',)
    ordering = ('-created_at',)
