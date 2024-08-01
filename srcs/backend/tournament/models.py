from django.db import models
from django.contrib.auth.models import User

# Create your models here.
# class Player(models.Model):
#     player_id = models.AutoField(primary_key=True)
#     username = models.CharField(max_length=255)
#     alias = models.CharField(max_length=255)
#     is_registered = models.BooleanField(default=False)
#     is_online = models.BooleanField(default=False)
#     auth_info = models.CharField(max_length=255)
#     current_tournament_id = models.IntegerField(null=True, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)

# class Match(models.Model):
#     game_id = models.AutoField(primary_key=True)
#     tournament = models.ForeignKey('Tournament', related_name='matches', on_delete=models.CASCADE)
#     player1 = models.ForeignKey(Player, related_name='player1_matches', on_delete=models.CASCADE)
#     player1_score = models.IntegerField()
#     player2 = models.ForeignKey(Player, related_name='player2_matches', on_delete=models.CASCADE)
#     player2_score = models.IntegerField()
#     state = models.CharField(max_length=255, default='pending')
#     winner = models.ForeignKey(Player, related_name='won_games', on_delete=models.CASCADE)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f'{self.player1.alias} vs {self.player2.alias}'
#     def winner(self):
#         if self.player1_score > self.player2_score:
#             return self.player1
#         return self.player2

# class Tournament(models.Model):
#     SIZE_CHOICES = [
#         (2, '2 Players'),
#         (4, '4 Players'),
#     ]

#     tournament_id = models.AutoField(primary_key=True)
#     name = models.CharField(max_length=255)
#     description = models.TextField()
#     size = models.IntegerField(choices=SIZE_CHOICES)
#     winner = models.ForeignKey(Player, related_name='tournaments_won', on_delete=models.SET_NULL)
#     created_at = models.DateTimeField(auto_now_add=True)
#     is_started = models.BooleanField(default=False)
#     is_final = models.BooleanField(default=False)
    
#     participants = models.ManyToManyField(Player, through='PlayerTournament')

#     def __str__(self):
#         return self.name
#     def start_tournament(self):
#         if self.size == self.participants.count():
#             self.create_1st_match()
#             self.is_started = True
#             self.save()
#     def create_1st_match(self):
#         # Create the first game
#         players = list(self.participants.all())
#         Match.objects.create(player1=players[0], player2=players[1], tournament=self)
    
#     def create_next_match(self):
#         if not self.is_final:
#             # Get the players who have not played yet
#             players = list(self.participants.all())
#             Match.objects.create(player1=players[2], player2=players[3], tournament=self)
#             self.is_final = True
#             self.save()
#         else:
#             # Get the winner of the tournament
#             winners = [game.winner() for game in self.matches.all()]
#             Match.objects.create(player1=winners[0], player2=winners[1], tournament=self)

# class PlayerTournament(models.Model):
#     player_tournament_id = models.AutoField(primary_key=True)
#     player = models.ForeignKey(Player, on_delete=models.CASCADE)
#     tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
#     created_at = models.DateTimeField(auto_now_add=True)

#TODO: to be replaced by real database
class Tournament(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    num_players = models.IntegerField(choices=[(2, '2'), (4, '4')])

    def __str__(self):
        return self.name

#TODO: to be replaced replace by real database
class Alias(models.Model):
    alias = models.CharField(max_length=100)

    def __str__(self):
        return self.name