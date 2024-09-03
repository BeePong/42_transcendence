import json
import logging
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.forms.models import model_to_dict
from django.conf import settings
import random
import math
import asyncio
import time
from asgiref.sync import sync_to_async

logging.basicConfig(level=logging.INFO)
from django.db.models.signals import post_save
from django.dispatch import receiver


class Player(models.Model):

    player_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, default=1
    )  # Replace 1 with an appropriate user ID
    username = models.CharField(max_length=255)
    # alias = models.CharField(max_length=255) #todo put the alias
    alias = models.CharField(max_length=100)
    has_active_tournament = models.BooleanField(
        default=False
    )  # active player in a tournament Rename has_active_tournament
    is_online = models.BooleanField(default=False)  #
    auth_info = models.CharField(max_length=255)
    current_tournament_id = models.IntegerField(null=True, blank=True, default=-1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username

    @receiver(post_save, sender=User)
    def create_player(sender, instance, created, **kwargs):
        if created:
            Player.objects.create(user=instance, username=instance.username)

    @receiver(post_save, sender=User)
    def save_player(sender, instance, **kwargs):
        instance.player.save()


class Tournament(models.Model):

    STATE_CHOICES = [
        ("NEW", "New"),
        ("PLAYING", "Started"),
        ("FINISHED", "Final"),
    ]

    tournament_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    state = models.CharField(max_length=50, choices=STATE_CHOICES, default="NEW")
    num_players = models.IntegerField()
    players = models.ManyToManyField(Player, related_name="tournaments", blank=True)
    # matches = models.ManyToManyField("Match", related_name="tournament", blank=True)

    # players = ArrayField(models.CharField(max_length=100), blank=True, default=list)

    # TODO: change to ForeignKey Player
    winner = models.ForeignKey(
        Player,
        related_name="won_tournaments",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_started = models.BooleanField(default=False)
    is_final = models.BooleanField(default=False)

    def __init__(self, *args, **kwargs):
        self.consumer = kwargs.pop("consumer", None)
        super().__init__(*args, **kwargs)
        self.game = None
        self.game_loop = None
        print("TOURNAMENT INITIALISED: ", self)

    def __str__(self):
        return json.dumps(self.__dict__, default=str)

    async def start_tournament_if_applicable(self):
        logging.info(f"Starting tournament {self.tournament_id} if applicable")
        num_players = await sync_to_async(self.players.count)()
        logging.info(f"Current players: {num_players}, Required players: {self.num_players}")

        if self.num_players == num_players and self.state == "PLAYING":
            logging.info("Conditions met to start the tournament")
            await self.create_1st_match()
            
            self.is_started = True
            await sync_to_async(self.save)()
            logging.info(f"Tournament {self.tournament_id} is_started set to True")

            # Start matches
            ordered_matches = self.matches.order_by("-created_at")
            matches = await sync_to_async(list)(ordered_matches)
            for match in matches:
                await match.start_match()
                logging.info(f"Started match {match.game_id}")

        else:
            logging.info(f"Conditions not met to start the tournament. State: {self.state}, Players: {num_players}/{self.num_players}")

    async def create_1st_match(self):
        logging.info(f"Creating first match(es) for tournament {self.tournament_id}")
        players = await sync_to_async(list)(self.players.all())
        num_players = len(players)

        if num_players == self.num_players:
            random.shuffle(players)
            if self.num_players == 2:
                match = await sync_to_async(Match.objects.create)(
                    player1=players[0], player2=players[1], tournament=self
                )
                logging.info(f"Created match {match.game_id} for 2 players")
                await sync_to_async(self.matches.add)(match)
            elif self.num_players == 4:
                match1 = await sync_to_async(Match.objects.create)(
                    player1=players[0], player2=players[1], tournament=self
                )
                match2 = await sync_to_async(Match.objects.create)(
                    player1=players[2], player2=players[3], tournament=self
                )
                logging.info(f"Created matches {match1.game_id} and {match2.game_id} for 4 players")
                await sync_to_async(self.matches.add)(match1)
                await sync_to_async(self.matches.add)(match2)
            else:
                logging.warning(f"Unsupported number of players: {self.num_players}")
                return

            await sync_to_async(self.save)()
            logging.info(f"First match(es) created for tournament {self.tournament_id}")
        else:
            logging.warning(f"Not enough players to create matches. Current: {num_players}, Required: {self.num_players}")

    def handle_key_action(self, user, key, keyAction):
        print("HANDLE KEY ACTION")
        player = self.get_user_in_tournament(user)
        print("got player in tournament: ", player.username)
        # TODO: change from first to actual match
        print("matches after")
        total_matches = self.matches.count()
        print("total matches: ", total_matches)
        # print all matches
        match = self.matches.first()
        print("match: ")
        if match:
            print(f"Match found, match for handling key id: {match.game_id}")
        else:
            print("No match found")
        # TODO: check match state
        match_player1 = match.player1.player_id
        match_player2 = match.player2.player_id
        print("match player 1: ", match_player1)
        print("match player 2: ", match_player2)
        if player.player_id == match_player1:
            print("key action player 1")
            if key == "ArrowUp":
                match.player1_up_pressed = keyAction == "keydown"
                match.player1_game_state["up_pressed"] = keyAction == "keydown"
                print("player 1 up pressed", match.player1_up_pressed)
            elif key == "ArrowDown":
                match.player1_down_pressed = keyAction == "keydown"
                match.player1_game_state["down_pressed"] = keyAction == "keydown"
                print("player 1 down pressed", match.player1_down_pressed)
        elif player.player_id == match_player2:
            print("key action player 2")
            if key == "ArrowUp":
                match.player2_up_pressed = keyAction == "keydown"
                match.player2_game_state["up_pressed"] = keyAction == "keydown"
                print("player 2 up pressed", match.player2_up_pressed)
            elif key == "ArrowDown":
                match.player2_down_pressed = keyAction == "keydown"
                match.player2_game_state["down_pressed"] = keyAction == "keydown"
                print("player 2 down pressed", match.player2_down_pressed)
        match.save()

    def is_user_in_tournament(self, user):
        resolved_user = self.resolve_user(user)
        return self.players.filter(user=resolved_user).exists()

    def resolve_user(self, user):
        if hasattr(user, "_wrapped") and hasattr(user, "_setup"):
            if not user._wrapped:
                user._setup()
            return user._wrapped
        return user

    def get_user_in_tournament(self, user):
        resolved_user = self.resolve_user(user)
        return self.players.get(user=resolved_user)

    def resolve_user(self, user):
        if hasattr(user, "_wrapped") and hasattr(user, "_setup"):
            if not user._wrapped:
                user._setup()
            return user._wrapped
        return user
        return self.players.get(user=user)

    @sync_to_async
    def connect_player_if_applicable(self, user):
        print("CONNECT PLAYER IF APPLICABLE")
        # if player is joining a new game, create a player for them
        # if self.state == "NEW" and self.players.count() < self.num_players:
        # TODO: remove duplicate with this logic in tournament_lobby views.py
        # player, _ = Player.objects.get_or_create(user=user)
        # player.is_online = True
        # player.username = user.username
        # if player.has_active_tournament == False:
        #    player.current_tournament_id = self.tournament_id
        #    player.has_active_tournament = True
        #    player.save()
        #    self.players.add(player)
        # if player is reconnecting mid-tournament, activate them
        if_user_in_tournament = self.is_user_in_tournament(user)
        if self.state == "PLAYING" and if_user_in_tournament:
            player = self.get_user_in_tournament(user)
            player.is_online = True
        self.save()

    @sync_to_async
    def disconnect_player(self, user):
        print("DISCONNECT PLAYER")
        if self.is_user_in_tournament(user):
            player = self.players.get(user=user)
            player.is_online = False
            player.save()

    @sync_to_async
    def create_next_match(self):
        print("CREATE NEXT MATCH")
        players = list(self.players.all())
        random.shuffle(players)
        if not self.is_final:
            if players.count() >= 4:

                match, created = Match.objects.get_or_create(
                    player1=players[0], player2=players[1], tournament=self
                )
                print("match created bool: ", created)
                logging.info(
                    "match created id: %s",
                    match.game_id,
                )
                self.matches.add(match)
                self.is_final = True
                self.save()
            else:
                # Handle cases where there aren't enough players
                pass
        else:
            winners = [game.winner() for game in self.matches.all()]
            if len(winners) >= 2:
                print("creating match")
                match = Match.objects.create(
                    player1=winners[0], player2=winners[1], tournament=self
                )
                logging.info(
                    "final match created id: %s",
                    match.game_id,
                )
                self.matches.add(match)
                self.save()


class GameLoop:

    def __init__(self, match):
        print("INIT GAME LOOP, match id: ", match.game_id)
        self.match = match
        self.running = True
        self.loop_task = None
        print("GAME LOOP INITIALIZED, match id: ", self.match.game_id)

    async def loop(self):
        if not self.loop_task or self.loop_task.done():
            self.loop_task = asyncio.create_task(self.game_loop())

    async def game_loop(self):
        from .consumers import PongConsumer

        print(
            "match ",
            self.match.game_id,
            ", tour. ",
            self.match.tournament.tournament_id,
            " GAME LOOP STARTED",
        )
        while self.running:
            # print("GAME LOOP RUNNING, state: ", self.match.state)
            if self.match.state == "COUNTDOWN":
                if time.time() - self.match.round_start_time <= 3:
                    # print("setting countdown")
                    self.match.countdown = 3 - int(
                        time.time() - self.match.round_start_time
                    )
                    # print("countdown: ", self.match.countdown)
                else:
                    self.match.countdown = 0
                    self.match.state = "PLAYING"
                    # print("state changed to PLAYING")
                await sync_to_async(self.match.save)()

            # Update the position of the paddles based on the key states
            # print("match: ", await self.match.to_dict())
            # print("MATCH ID: ", self.match.game_id)
            if (
                self.match.player1_up_pressed
                or self.match.player1_game_state["up_pressed"]
            ):
                new_y = self.match.player1_y - settings.PADDLE_SPEED
                if new_y < settings.UPPER_LIMIT:
                    self.match.player1_y = settings.UPPER_LIMIT
                else:
                    self.match.player1_y = new_y
                print("new y player 1: ", self.match.player1_y)
            elif (
                self.match.player1_down_pressed
                or self.match.player1_game_state["down_pressed"]
            ):
                new_y = self.match.player1_y + settings.PADDLE_SPEED
                if new_y > settings.LOWER_LIMIT:
                    self.match.player1_y = settings.LOWER_LIMIT
                else:
                    self.match.player1_y = new_y
                print("new y player 1: ", self.match.player1_y)
            # print("UPDATING PADDLE POSITIONS 2")
            if (
                self.match.player2_up_pressed
                or self.match.player2_game_state["up_pressed"]
            ):
                new_y = self.match.player2_y - settings.PADDLE_SPEED
                if new_y < settings.UPPER_LIMIT:
                    self.match.player2_y = settings.UPPER_LIMIT
                else:
                    self.match.player2_y = new_y
                print("new y player 2: ", self.match.player2_y)

            elif (
                self.match.player2_down_pressed
                or self.match.player2_game_state["down_pressed"]
            ):
                new_y = self.match.player2_y + settings.PADDLE_SPEED
                if new_y > settings.LOWER_LIMIT:
                    self.match.player2_y = settings.LOWER_LIMIT
                else:
                    self.match.player2_y = new_y
                print("new y player 2: ", self.match.player2_y)
            # print("BALL UPDATE PLAYING")
            if self.match.state == "PLAYING":
                # Calculate next position of the ball
                ball_new_x = (
                    self.match.ball["x"]
                    + self.match.ball_speed * self.match.ball_vector["x"]
                )
                ball_new_y = (
                    self.match.ball["y"]
                    + self.match.ball_speed * self.match.ball_vector["y"]
                )
                # print("BALL NEW X: ", ball_new_x)
                # print("BALL NEW Y: ", ball_new_y)
                # Check for collisions with the game boundaries
                if ball_new_y <= settings.THICK_BORDER_THICKNESS + settings.BALL_RADIUS:
                    # print("checking y upper collision")
                    # Calculate the remaining movement after the ball hits the wall
                    remaining_movement = (
                        settings.THICK_BORDER_THICKNESS
                        + settings.BALL_RADIUS
                        - self.match.ball["y"]
                    )
                    # Reverse the y-component of the ball's direction vector
                    self.match.ball_vector["y"] *= -1
                    # Move the ball the remaining distance in the new direction
                    ball_new_y = (
                        self.match.ball["y"]
                        + remaining_movement * self.match.ball_vector["y"]
                    )
                elif (
                    ball_new_y
                    >= settings.FIELD_HEIGHT
                    - settings.THICK_BORDER_THICKNESS
                    - settings.BALL_RADIUS
                ):
                    # print("checking y lower collision")
                    # Calculate the remaining movement after the ball hits the wall
                    remaining_movement = (
                        self.match.ball["y"]
                        + settings.BALL_RADIUS
                        - (settings.FIELD_HEIGHT - settings.THICK_BORDER_THICKNESS)
                    )
                    # Reverse the y-component of the ball's direction vector
                    self.match.ball_vector["y"] *= -1
                    # Move the ball the remaining distance in the new direction
                    ball_new_y = (
                        self.match.ball["y"]
                        - remaining_movement * self.match.ball_vector["y"]
                    )
                # print("after checking collisions with game boundaries")
                # Collisions with the paddles
                if (
                    ball_new_x
                    < settings.PADDING_THICKNESS
                    + settings.PADDLE_WIDTH
                    + settings.BALL_RADIUS
                    and self.match.player2_y
                    - settings.PADDLE_HEIGHT / 2
                    - settings.BALL_RADIUS
                    <= ball_new_y
                    <= self.match.player2_y
                    + settings.PADDLE_HEIGHT / 2
                    + settings.BALL_RADIUS
                ):
                    print(
                        "match ",
                        self.match.game_id,
                        ", tour. ",
                        self.match.tournament.tournament_id,
                        "HIT LEFT PADDLE",
                    )
                    self.match.hit_count += 1
                    self.match.ball_speed += settings.BALL_SPEED_INCREMENT
                    # Calculate the remaining movement after the ball hits the wall
                    remaining_movement = (
                        settings.PADDING_THICKNESS
                        + settings.PADDLE_WIDTH
                        + settings.BALL_RADIUS
                        - self.match.ball["x"]
                    )
                    # check if ball is moving towards the paddle
                    if self.match.ball_vector["x"] < 0:
                        # Reverse the x-component of the ball's direction vector
                        self.match.ball_vector["x"] *= -1
                        # Move the ball the remaining distance in the new direction
                        ball_new_x = (
                            self.match.ball["x"]
                            + remaining_movement * self.match.ball_vector["x"]
                        )
                if (
                    ball_new_x
                    > settings.FIELD_WIDTH
                    - settings.PADDING_THICKNESS
                    - settings.PADDLE_WIDTH
                    - settings.BALL_RADIUS
                    and self.match.player1_y
                    - settings.PADDLE_HEIGHT / 2
                    - settings.BALL_RADIUS
                    <= ball_new_y
                    <= self.match.player1_y
                    + settings.PADDLE_HEIGHT / 2
                    + settings.BALL_RADIUS
                ):
                    print(
                        "match ",
                        self.match.game_id,
                        ", tour. ",
                        self.match.tournament.tournament_id,
                        "HIT RIGHT PADDLE",
                    )
                    self.match.hit_count += 1
                    self.match.ball_speed += settings.BALL_SPEED_INCREMENT
                    # Calculate the remaining movement after the ball hits the wall
                    remaining_movement = (
                        self.match.ball["x"]
                        + settings.BALL_RADIUS
                        - (
                            settings.FIELD_WIDTH
                            - settings.PADDING_THICKNESS
                            - settings.PADDLE_WIDTH
                        )
                    )
                    # check  if ball is moving towards the paddle
                    if self.match.ball_vector["x"] > 0:
                        # Reverse the x-component of the ball's direction vector
                        self.match.ball_vector["x"] *= -1
                        # Move the ball the remaining distance in the new direction
                        ball_new_x = (
                            self.match.ball["x"]
                            - remaining_movement * self.match.ball_vector["x"]
                        )
                # print("after checking collisions with paddles")
                # Update the ball's position
                self.match.ball["x"] = ball_new_x
                self.match.ball["y"] = ball_new_y

                # Check for scoring
                if ball_new_x >= settings.FIELD_WIDTH - settings.BALL_RADIUS:
                    print(
                        "match ",
                        self.match.game_id,
                        ", tour. ",
                        self.match.tournament.tournament_id,
                        "PLAYER 1 SCORED",
                    )
                    self.match.player1_score += 1
                    await sync_to_async(self.match.init_new_round)()
                    if self.match.player1_score == settings.MAX_SCORE:
                        self.match.winner = self.match.player1
                        self.match.state = "FINISHED"
                        self.match.player2_score = 0
                        self.match.player1_score = 0
                    await sync_to_async(self.match.save)()
                elif ball_new_x <= settings.BALL_RADIUS:
                    print(
                        "match ",
                        self.match.game_id,
                        ", tour. ",
                        self.match.tournament.tournament_id,
                        "PLAYER 2 SCORED",
                    )
                    self.match.player2_score += 1
                    await sync_to_async(self.match.init_new_round)()
                    if self.match.player2_score == settings.MAX_SCORE:
                        self.match.winner = self.match.player2
                        self.match.state = "FINISHED"
                        self.match.player2_score = 0
                        self.match.player1_score = 0
                    await sync_to_async(self.match.save)()
            # will this find the correct consumer?
            # print("SENDING GAME STATE TO ALL")
            await self.match.tournament.consumer.send_game_state_to_all(self.match)
            # print("GAME STATE SENT TO ALL")
            await asyncio.sleep(1 / settings.FPS)
            # print("GAME LOOP AFTER SLEEPING")
            if self.match.state == "FINISHED":
                print(
                    "match ",
                    self.match.game_id,
                    ", tour. ",
                    self.match.tournament.tournament_id,
                    "MATCH FINISHED",
                )
                self.stop()

    def stop(self):
        print(
            "match ",
            self.match.game_id,
            ", tour. ",
            self.match.tournament.tournament_id,
            "STOP GAME LOOP",
        )
        self.running = False
        if self.loop_task:
            self.loop_task.cancel()
            self.loop_task = None


class Match(models.Model):

    STATE_CHOICES = [
        ("PENDING", "Pending"),
        ("COUNTDOWN", "New"),
        ("PLAYING", "Started"),
        ("FINISHED", "Final"),
    ]

    game_id = models.AutoField(primary_key=True)
    tournament = models.ForeignKey(
        Tournament, related_name="matches", on_delete=models.CASCADE
    )
    player1 = models.ForeignKey(
        Player, related_name="player1_matches", on_delete=models.CASCADE
    )
    player1_score = models.IntegerField(default=0)
    player1_up_pressed = models.BooleanField(default=False)
    player1_down_pressed = models.BooleanField(default=False)
    player1_y = models.IntegerField(default=settings.FIELD_HEIGHT / 2)
    player2 = models.ForeignKey(
        Player, related_name="player2_matches", on_delete=models.CASCADE
    )
    player2_score = models.IntegerField(default=0)
    player2_up_pressed = models.BooleanField(default=False)
    player2_down_pressed = models.BooleanField(default=False)
    player2_y = models.IntegerField(default=settings.FIELD_HEIGHT / 2)
    state = models.CharField(max_length=255, choices=STATE_CHOICES, default="PENDING")
    winner = models.ForeignKey(
        Player,
        related_name="won_games",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def get_larger_random(self):
        y = 0
        while abs(y) < 0.2 or abs(y) > 0.9:
            y = random.uniform(-1, 1)
        return y

    def normalize_vector(self, x, y):
        magnitude = math.sqrt(x**2 + y**2)
        return {"x": x / magnitude, "y": y / magnitude}

    def __init__(self, *args, **kwargs):
        print("INIT MATCH")
        super().__init__(*args, **kwargs)
        print("tournament", kwargs.get("tournament"))
        print("player1", kwargs.get("player1"))
        print("player2", kwargs.get("player2"))
        self.countdown = 3
        self.ball = {"x": settings.FIELD_WIDTH / 2, "y": settings.FIELD_HEIGHT / 2}
        self.ball_speed = settings.BALL_STARTING_SPEED
        self.hit_count = 0
        self.ball_vector = self.normalize_vector(
            self.get_larger_random(), random.uniform(-1, 1)
        )
        self.player1_game_state = {
            "y": settings.FIELD_HEIGHT / 2,
            "up_pressed": False,
            "down_pressed": False,
        }
        self.player2_game_state = {
            "y": settings.FIELD_HEIGHT / 2,
            "up_pressed": False,
            "down_pressed": False,
        }
        print("MATCH INITIALIZED")
        self.game_loop = GameLoop(self)
        self.round_start_time = time.time()
        all_matches = Match.objects.all()
        num_all_matches = all_matches.count()
        print("end of INIT MATCH num all matches: ", num_all_matches)
        print("GAME LOOP IN MATCH INITIALIZED")

    def __str__(self):
        return f"{self.player1.alias} vs {self.player2.alias}"

    async def start_match(self):
        print("START MATCH")
        self.state = "COUNTDOWN"
        self.round_start_time = time.time()
        await self.game_loop.loop()
        await sync_to_async(self.save)()

    def determine_winner(self):
        print("DETERMINE WINNER")
        if self.player1_score > self.player2_score:
            return self.player1
        return self.player2

    def determine_loser(self):
        print("DETERMINE LOSER")
        if self.player1_score < self.player2_score:
            return self.player1
        return self.player2

    def init_new_round(self):
        print("INIT NEW ROUND")
        self.round_start_time = time.time()
        self.state = "COUNTDOWN"
        self.countdown = 3
        self.hit_count = 0
        self.ball = {"x": settings.FIELD_WIDTH / 2, "y": settings.FIELD_HEIGHT / 2}
        self.ball_speed = settings.BALL_STARTING_SPEED
        self.hit_count = 0
        self.ball_vector = self.normalize_vector(
            self.get_larger_random(), random.uniform(-1, 1)
        )
        self.save()
        print("NEW ROUND INITIALIZED")

    def init_new_game(self):
        print("INIT NEW GAME")
        self.init_new_round()
        self.player1_score = 0
        self.player2_score = 0
        self.winner = None
        self.state = "PENDING"
        self.save()

    @sync_to_async
    def to_dict(self):
        return {
            "round_start_time": self.round_start_time,
            "state": self.state,
            "countdown": self.countdown,
            "ball": self.ball,
            "ball_speed": self.ball_speed,
            "hit_count": self.hit_count,
            "ball_vector": self.ball_vector,
            "player1": {
                "player_id": self.player1.player_id,
                "player_name": self.player1.username,
                "score": self.player1_score,
                "y": self.player1_y,
                "up_pressed": self.player1_up_pressed,
                "down_pressed": self.player1_down_pressed,
            },
            "player2": {
                "player_id": self.player2.player_id,
                "player_name": self.player2.username,
                "score": self.player2_score,
                "y": self.player2_y,
                "up_pressed": self.player2_up_pressed,
                "down_pressed": self.player2_down_pressed,
            },
            "winner": self.winner,
        }


class PlayerTournament(models.Model):
    player_tournament_id = models.AutoField(primary_key=True)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
