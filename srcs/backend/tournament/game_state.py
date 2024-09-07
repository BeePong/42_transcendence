from django.conf import settings
import random
import time
import json
from .utils import get_larger_random, normalize_vector


class Ball:
    def __init__(self, x=settings.FIELD_WIDTH / 2, y=settings.FIELD_HEIGHT / 2):
        self.x = x
        self.y = y

    def __str__(self):
        return json.dumps(self.__dict__, default=str)

    def to_dict(self):
        return {"x": self.x, "y": self.y}


class GamePlayer:
    def __init__(
        self,
        player_id,
        player_name,
        y=settings.FIELD_HEIGHT / 2,
        up_pressed=False,
        down_pressed=False,
    ):
        self.player_id = player_id
        self.player_name = player_name
        self.y = y
        self.up_pressed = up_pressed
        self.down_pressed = down_pressed

    def __str__(self):
        return json.dumps(self.__dict__, default=str)

    def to_dict(self):
        return {
            "player_id": self.player_id,
            "player_name": self.player_name,
            "y": self.y,
            "up_pressed": self.up_pressed,
            "down_pressed": self.down_pressed,
        }


class GameState:
    def __init__(self, match, tournament):
        print("INIT GAME STATE")
        if tournament is None:
            raise ValueError("tournament cannot be None")
        self.tournament = tournament
        self.state = "NEW"
        if match is None:
            raise ValueError("match cannot be None")
        self.match = match
        # init game state
        self.round_start_time = time.time()
        self.countdown = settings.COUNTDOWN_TIME
        self.ball = Ball()
        self.ball_speed = settings.BALL_STARTING_SPEED
        self.hit_count = 0
        self.ball_vector = normalize_vector(get_larger_random(), random.uniform(-1, 1))
        self.player1 = GamePlayer(
            self.match.player1.player_id,
            self.match.player1.alias,
        )
        self.player2 = GamePlayer(
            self.match.player2.player_id,
            self.match.player2.alias,
        )
        print("MATCH INITIALIZED")

    def __str__(self):
        return json.dumps(self.__dict__, default=str)

    def to_dict(self):
        return {
            "curr_time": time.time(),
            "round_start_time": self.round_start_time,
            "state": self.state,
            "countdown": self.countdown,
            "ball": self.ball.to_dict(),
            "ball_speed": self.ball_speed,
            "hit_count": self.hit_count,
            "ball_vector": self.ball_vector,
            "player1": self.player1.to_dict(),
            "player2": self.player2.to_dict(),
            # winner?
        }
