import json

from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.forms.models import model_to_dict
from django.conf import settings
import random
import math
import asyncio
from .consumers import PongConsumer
import time

class Player(models.Model):
    player_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, default=1
    )  # Replace 1 with an appropriate user ID
    username = models.CharField(max_length=255)
    alias = models.CharField(max_length=255)  # todo put the alias
    has_active_tournament = models.BooleanField(
        default=False
    )  # active player in a tournament Rename has_active_tournament
    is_online = models.BooleanField(default=False)  #
    auth_info = models.CharField(max_length=255)
    current_tournament_id = models.IntegerField(null=True, blank=True, default=-1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return json.dumps(model_to_dict(self))


class Tournament(models.Model):
    STATE_CHOICES = [
        ("NEW", "New"),
        ("READY", "Ready"),
        ("PLAYING", "Started"),
        ("FINISHED", "Final"),
        # Add more states as needed
    ]

    tournament_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    state = models.CharField(max_length=50, choices=STATE_CHOICES, default="NEW")
    num_players = models.IntegerField()
    # num_players_in = models.IntegerField(default=0)
    players = models.ManyToManyField(Player, related_name="tournaments", blank=True)
    matches = models.ManyToManyField("Match", related_name="tournament", blank=True)

    # players = ArrayField(models.CharField(max_length=100), blank=True, default=list)

    winner = models.CharField(max_length=255, null=True, blank=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    is_started = models.BooleanField(default=False)
    is_final = models.BooleanField(default=False)

    async def __init__(self, tournament_id):
        self.game = None
        self.game_loop = None
        print("TOURNAMENT INITIALISED, id: ", tournament_id)

    def __str__(self):
        return json.dumps(self.__dict__, default=str)

    def start_tournament_if_applicable(self):
        if self.num_players == len(self.players):
            self.create_1st_match()
            self.is_started = True
            self.save()

    def is_user_in_tournament(self, user):
        return self.players.filter(user=user).exists()

    def get_user_in_tournament(self, user):
        return self.players.get(user=user)

    def connect_player_if_applicable(self, user):
        # if player is joining a new game, create a player for them
        if self.tournament.state == "NEW" and len(self.players) < self.num_players:
            player, _ = Player.objects.create(user=user, is_online=True)
            self.players.add(player)
            if len(self.players) == self.num_players:
                self.state = "READY"
                self.start_tournament()
        # if player is reconnecting mid-tournament, activate them
        elif self.tournament.state == "PLAYING" and self.is_user_in_tournament(user):
            player = self.get_user_in_tournament(user)
            player.is_online = True
        self.save()

    def disconnect_player(self, user):
        if self.is_user_in_tournament(user):
            player = self.players.get(user=user)
            player.is_online = False
            player.save()

    def create_1st_match(self):
        if len(self.players) >= 2:
            Match.objects.create(
                player1=self.players[0], player2=self.players[1], tournament=self
            )

    def create_next_match(self):
        if not self.is_final:
            if len(self.players) >= 4:
                Match.objects.create(
                    player1=self.players[2], player2=self.players[3], tournament=self
                )
                self.is_final = True
                self.save()
            else:
                # Handle cases where there aren't enough players
                pass
        else:
            winners = [game.winner() for game in self.matches.all()]
            if len(winners) >= 2:
                Match.objects.create(
                    player1=winners[0], player2=winners[1], tournament=self
                )

class GameLoop:

    def __init__(self, match):
        self.match = match
        self.running = True
        self.loop_task = None
        print("GAME LOOP INITIALIZED")

    def start(self):
        self.loop_task = asyncio.create_task(self.game_loop())

    async def loop(self):
        self.loop_task = asyncio.create_task(self.game_loop())

    async def game_loop(self):
        print("GAME LOOP STARTED")
        # Your game loop code here, which can use self.game_state
        while self.running:
            if self.match["state"] == :
                if time.time() - self.match["round_start_time"] <= 3:
                    self.match["countdown"] = 3 - int(
                        time.time() - self.match["round_start_time"]
                    )
                else:
                    self.match["countdown"] = 0
                    self.match["state"] = "playing"

            # Update the position of the paddles based on the key states
            for player_id in ["player1", "player2"]:
                if self.match[player_id]["up_pressed"]:
                    new_y = self.match[player_id]["y"] - settings.PADDLE_SPEED
                    if new_y < settings.UPPER_LIMIT:
                        self.match[player_id]["y"] = settings.UPPER_LIMIT
                    else:
                        self.match[player_id]["y"] = new_y

                elif self.match[player_id]["down_pressed"]:
                    new_y = self.match[player_id]["y"] + settings.PADDLE_SPEED
                    if new_y > settings.LOWER_LIMIT:
                        self.match[player_id]["y"] = settings.LOWER_LIMIT
                    else:
                        self.match[player_id]["y"] = new_y

            if self.match["state"] == "playing":
                # Calculate next position of the ball
                ball_new_x = (
                    self.match["ball"]["x"]
                    + self.match["ball_speed"]
                    * self.match["ball_vector"]["x"]
                )
                ball_new_y = (
                    self.match["ball"]["y"]
                    + self.match["ball_speed"]
                    * self.match["ball_vector"]["y"]
                )

                # Check for collisions with the game boundaries
                if ball_new_y <= settings.THICK_BORDER_THICKNESS + settings.BALL_RADIUS:
                    # Calculate the remaining movement after the ball hits the wall
                    remaining_movement = (
                        settings.THICK_BORDER_THICKNESS
                        + settings.BALL_RADIUS
                        - self.match["ball"]["y"]
                    )
                    # Reverse the y-component of the ball's direction vector
                    self.match["ball_vector"]["y"] *= -1
                    # Move the ball the remaining distance in the new direction
                    ball_new_y = (
                        self.match["ball"]["y"]
                        + remaining_movement * self.match["ball_vector"]["y"]
                    )
                elif (
                    ball_new_y
                    >= settings.FIELD_HEIGHT
                    - settings.THICK_BORDER_THICKNESS
                    - settings.BALL_RADIUS
                ):
                    # Calculate the remaining movement after the ball hits the wall
                    remaining_movement = (
                        self.match["ball"]["y"]
                        + settings.BALL_RADIUS
                        - (settings.FIELD_HEIGHT - settings.THICK_BORDER_THICKNESS)
                    )
                    # Reverse the y-component of the ball's direction vector
                    self.match["ball_vector"]["y"] *= -1
                    # Move the ball the remaining distance in the new direction
                    ball_new_y = (
                        self.match["ball"]["y"]
                        - remaining_movement * self.match["ball_vector"]["y"]
                    )

                # Collisions with the paddles
                if (
                    ball_new_x
                    < settings.PADDING_THICKNESS
                    + settings.PADDLE_WIDTH
                    + settings.BALL_RADIUS
                    and self.match["player2"]["y"]
                    - settings.PADDLE_HEIGHT / 2
                    - settings.BALL_RADIUS
                    <= ball_new_y
                    <= self.match["player2"]["y"]
                    + settings.PADDLE_HEIGHT / 2
                    + settings.BALL_RADIUS
                ):
                    # print("HIT LEFT PADDLE")
                    self.match["hit_count"] += 1
                    self.match["ball_speed"] += settings.BALL_SPEED_INCREMENT
                    # Calculate the remaining movement after the ball hits the wall
                    remaining_movement = (
                        settings.PADDING_THICKNESS
                        + settings.PADDLE_WIDTH
                        + settings.BALL_RADIUS
                        - self.match["ball"]["x"]
                    )
                    # check if ball is moving towards the paddle
                    if self.match["ball_vector"]["x"] < 0:
                        # Reverse the x-component of the ball's direction vector
                        self.match["ball_vector"]["x"] *= -1
                        # Move the ball the remaining distance in the new direction
                        ball_new_x = (
                            self.match["ball"]["x"]
                            + remaining_movement * self.match["ball_vector"]["x"]
                        )
                if (
                    ball_new_x
                    > settings.FIELD_WIDTH
                    - settings.PADDING_THICKNESS
                    - settings.PADDLE_WIDTH
                    - settings.BALL_RADIUS
                    and self.match["player1"]["y"]
                    - settings.PADDLE_HEIGHT / 2
                    - settings.BALL_RADIUS
                    <= ball_new_y
                    <= self.match["player1"]["y"]
                    + settings.PADDLE_HEIGHT / 2
                    + settings.BALL_RADIUS
                ):
                    self.match["hit_count"] += 1
                    self.match["ball_speed"] += settings.BALL_SPEED_INCREMENT
                    # Calculate the remaining movement after the ball hits the wall
                    remaining_movement = (
                        self.match["ball"]["x"]
                        + settings.BALL_RADIUS
                        - (
                            settings.FIELD_WIDTH
                            - settings.PADDING_THICKNESS
                            - settings.PADDLE_WIDTH
                        )
                    )
                    # check  if ball is moving towards the paddle
                    if self.match["ball_vector"]["x"] > 0:
                        # Reverse the x-component of the ball's direction vector
                        self.match["ball_vector"]["x"] *= -1
                        # Move the ball the remaining distance in the new direction
                        ball_new_x = (
                            self.match["ball"]["x"]
                            - remaining_movement * self.match["ball_vector"]["x"]
                        )

                # Update the ball's position
                self.match["ball"]["x"] = ball_new_x
                self.match["ball"]["y"] = ball_new_y

                # Check for scoring
                if ball_new_x >= settings.FIELD_WIDTH - settings.BALL_RADIUS:
                    print("PLAYER 1 SCORED")
                    self.match["player1_score"] += 1
                    self.match.get_instance().init_new_round()
                    if self.match["player1_score"] == settings.MAX_SCORE:
                        self.match["winner"] = self.match.player1
                        self.match["state"] = "finished"
                        self.match["player2_score"] = 0
                        self.match["player1_score"] = 0
                elif ball_new_x <= settings.BALL_RADIUS:
                    print("PLAYER 2 SCORED")
                    self.match["player2_score"] += 1
                    self.match.init_new_round()
                    if self.match["player2_score"] == settings.MAX_SCORE:
                        self.match["winner"] = self.match.player2
                        self.match["state"] = "finished"
                        self.match["player2_score"] = 0
                        self.match["player1_score"] = 0
            # will this find the correct consumer?
            await PongConsumer.send_game_state_to_all()
            await asyncio.sleep(1 / settings.FPS)

    def stop(self):
        self.running = False
        if self.loop_task:
            self.loop_task.cancel()

class Match(models.Model):
    game_id = models.AutoField(primary_key=True)
    tournament = models.ForeignKey(
        Tournament, related_name="matches", on_delete=models.CASCADE
    )
    player1 = models.ForeignKey(
        Player, related_name="player1_matches", on_delete=models.CASCADE
    )
    player1_score = models.IntegerField()
    player2 = models.ForeignKey(
        Player, related_name="player2_matches", on_delete=models.CASCADE
    )
    player2_score = models.IntegerField()
    state = models.CharField(max_length=255, default="pending")
    winner = models.ForeignKey(
        Player, related_name="won_games", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def get_larger_random(self):
        y = 0
        while abs(y) < 0.2:
            y = random.uniform(-1, 1)
        return y

    def normalize_vector(self, x, y):
        magnitude = math.sqrt(x**2 + y**2)
        return {"x": x / magnitude, "y": y / magnitude}

    def __init__(self):
        self.countdown = 3
        self.ball = {
            "x": settings.FIELD_WIDTH / 2,
            "y": settings.FIELD_HEIGHT / 2
        }
        self.ball_speed = settings.BALL_STARTING_SPEED
        self.hit_count = 0
        self.ball_vector = self.normalize_vector(
            self.get_larger_random(),
            random.uniform(-1, 1)
        )
        self.player1 = {
            "y": settings.FIELD_HEIGHT / 2,
            "up_pressed": False,
            "down_pressed": False
        }
        self.player2 = {
            "y": settings.FIELD_HEIGHT / 2,
            "up_pressed": False,
            "down_pressed": False
        }
        self.game_loop = GameLoop(self)

    def __str__(self):
        return f"{self.player1.alias} vs {self.player2.alias}"

    async def start_match(self):
        await self.game_loop = GameLoop.loop()

    def determine_winner(self):
        if self.player1_score > self.player2_score:
            return self.player1
        return self.player2

    def determine_loser(self):
        if self.player1_score < self.player2_score:
            return self.player1
        return self.player2


class PlayerTournament(models.Model):
    player_tournament_id = models.AutoField(primary_key=True)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


##TODO: to be replaced replace by real database
class Alias(models.Model):
    alias = models.CharField(max_length=100)

    def __str__(self):
        return self.name
