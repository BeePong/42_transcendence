from django.db import models

# Create your models here.
class Player(models.Model):
    player_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=255)
    alias = models.CharField(max_length=255)
    is_registered = models.BooleanField(default=False)
    is_online = models.BooleanField(default=False)
    auth_info = models.CharField(max_length=255)
    current_tournament_id = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Game(models.Model):
    game_id = models.AutoField(primary_key=True)
    player1 = models.ForeignKey(Player, related_name='player1_games', on_delete=models.CASCADE)
    player1_score = models.IntegerField()
    player2 = models.ForeignKey(Player, related_name='player2_games', on_delete=models.CASCADE)
    player2_score = models.IntegerField()
    state = models.CharField(max_length=255)
    winner = models.ForeignKey(Player, related_name='won_games', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class Tournament(models.Model):
    tournament_id = models.AutoField(primary_key=True)
    quarter1 = models.ForeignKey(Game, related_name='quarter1_games', null=True, blank=True, on_delete=models.SET_NULL)
    quarter2 = models.ForeignKey(Game, related_name='quarter2_games', null=True, blank=True, on_delete=models.SET_NULL)
    quarter3 = models.ForeignKey(Game, related_name='quarter3_games', null=True, blank=True, on_delete=models.SET_NULL)
    quarter4 = models.ForeignKey(Game, related_name='quarter4_games', null=True, blank=True, on_delete=models.SET_NULL)
    semi1 = models.ForeignKey(Game, related_name='semi1_games', null=True, blank=True, on_delete=models.SET_NULL)
    semi2 = models.ForeignKey(Game, related_name='semi2_games', null=True, blank=True, on_delete=models.SET_NULL)
    final = models.ForeignKey(Game, related_name='final_games', null=True, blank=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=255)
    description = models.TextField()
    state = models.CharField(max_length=255)
    num_players = models.IntegerField()
    winner = models.ForeignKey(Player, related_name='tournaments_won', null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

class PlayerTournament(models.Model):
    player_tournament_id = models.AutoField(primary_key=True)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)