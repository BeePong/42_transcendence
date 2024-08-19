from django.contrib import admin
from .models import Player, Tournament, Match, PlayerTournament, Alias

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('username', 'alias', 'has_active_tournament', 'is_online', 'current_tournament_id', 'created_at')
    search_fields = ('username', 'alias')

@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ('title', 'state', 'num_players', 'num_players_in', 'is_started', 'is_final', 'created_at')
    search_fields = ('title',)
    list_filter = ('state', 'is_started', 'is_final')

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('tournament', 'player1', 'player2', 'state', 'winner', 'created_at')
    search_fields = ('tournament__title', 'player1__username', 'player2__username')
    list_filter = ('state',)

@admin.register(PlayerTournament)
class PlayerTournamentAdmin(admin.ModelAdmin):
    list_display = ('player', 'tournament', 'created_at')
    search_fields = ('player__username', 'tournament__title')

@admin.register(Alias)
class AliasAdmin(admin.ModelAdmin):
    list_display = ('alias',)
    search_fields = ('alias',)
