import json
import logging
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField

logging.basicConfig(level=logging.INFO)


class Player(models.Model):

    player_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="player")
    username = models.CharField(max_length=255)
    alias = models.CharField(max_length=100)
    has_active_tournament = models.BooleanField(default=False)
    is_online = models.BooleanField(default=False)  #
    current_tournament_id = models.IntegerField(null=True, blank=True, default=-1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return json.dumps(self.__dict__, default=str)

    @receiver(post_save, sender=User)
    def create_player(sender, instance, created, **kwargs):
        if created:
            Player.objects.create(user=instance, username=instance.username)

    @receiver(post_save, sender=User)
    def save_player(sender, instance, **kwargs):
        instance.player.save()


class Match(models.Model):

    STATE_CHOICES = [
        ("NEW", "New"),
        ("COUNTDOWN", "Countdown"),
        ("PLAYING", "Playing"),
        ("FINISHED", "Finished"),
    ]

    game_id = models.AutoField(primary_key=True)
    player1 = models.ForeignKey(
        Player, related_name="player1_matches", on_delete=models.CASCADE
    )
    player2 = models.ForeignKey(
        Player, related_name="player2_matches", on_delete=models.CASCADE
    )
    state = models.CharField(max_length=255, choices=STATE_CHOICES, default="NEW")
    winner = models.ForeignKey(
        Player,
        related_name="won_games",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    tournament = models.ForeignKey(
        "Tournament", related_name="matches", on_delete=models.CASCADE
    )

    def __str__(self):
        return json.dumps(self.__dict__, default=str)

    def determine_loser(self):
        if self.winner == self.player1:
            return self.player2
        return self.player1


class Tournament(models.Model):

    STATE_CHOICES = [
        ("NEW", "New"),
        ("COUNTDOWN", "Countdown"),
        ("PLAYING", "Started"),
        ("FINISHED", "Final"),
    ]

    tournament_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    state = models.CharField(max_length=50, choices=STATE_CHOICES, default="NEW")
    num_players = models.IntegerField()
    players = models.ManyToManyField(Player, related_name="tournaments", blank=True)
    winner = models.ForeignKey(
        Player,
        related_name="won_tournaments",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    is_started = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_final = models.BooleanField(default=False)  # do we need this? yes for the signal
    current_match = models.ForeignKey(
        Match,
        related_name="current_tournament",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    def __str__(self):
        return json.dumps(self.__dict__, default=str)

    def is_full(self):
        return self.players.count() == self.num_players

    def get_matches_by_id(self, match_id):
        return self.matches.filter(id=match_id)
