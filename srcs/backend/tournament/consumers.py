import json
import math
import random
import threading
import time
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from enum import Enum
from django.conf import settings

# from django.contrib.auth.models import User

from .models import Tournament, Player
from django.shortcuts import get_object_or_404
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer

# import asyncio
# from .ai import ai_bot


class GameState(Enum):
    COUNTDOWN = "countdown"
    PLAYING = "playing"
    FINISHED = "finished"


class Game:
    def __init__(self):
        self.game_state = {
            "round_start_time": time.time(),
            "state": GameState.COUNTDOWN.value,
            "countdown": 3,
            "ball": {"x": settings.FIELD_WIDTH / 2, "y": settings.FIELD_HEIGHT / 2},
            "ball_speed": settings.BALL_STARTING_SPEED,
            "hit_count": 0,
            "ball_vector": self.normalize_vector(
                self.get_larger_random(), random.uniform(-1, 1)
            ),
            "player1": {
                "player_id": None,
                "player_name": "vvagapov",
                "score": 0,
                "y": settings.FIELD_HEIGHT / 2,
                "up_pressed": False,
                "down_pressed": False,
            },
            "player2": {
                "player_id": None,
                "player_name": "dummy",
                "score": 0,
                "y": settings.FIELD_HEIGHT / 2,
                "up_pressed": False,
                "down_pressed": False,
            },
            "winner": None,
        }
        self.tournament = None

    def get_larger_random(self):
        y = 0
        while abs(y) < 0.2:
            y = random.uniform(-1, 1)
        return y

    def normalize_vector(self, x, y):
        magnitude = math.sqrt(x**2 + y**2)
        return {"x": x / magnitude, "y": y / magnitude}

    def init_new_round(self):
        self.game_state["round_start_time"] = time.time()
        self.game_state["state"] = GameState.COUNTDOWN.value
        self.game_state["countdown"] = 3
        self.game_state["hit_count"] = 0
        self.game_state["ball"] = {
            "x": settings.FIELD_WIDTH / 2,
            "y": settings.FIELD_HEIGHT / 2,
        }
        self.game_state["ball_speed"] = settings.BALL_STARTING_SPEED
        self.game_state["hit_count"] = 0
        self.game_state["ball_vector"] = self.normalize_vector(
            self.get_larger_random(), random.uniform(-1, 1)
        )
        print("NEW ROUND INITIALIZED")

    def init_new_game(self):
        self.init_new_round()
        self.game_state["player1"]["score"]
        self.game_state["player1"]["player_id"] = None
        self.game_state["player2"]["score"]
        self.game_state["player2"]["player_id"] = None
        self.game_state["winner"] = None


class PongConsumer(AsyncWebsocketConsumer):

    tournament = None
    print("PONG CONSUMER CREATED")

    @database_sync_to_async
    def get_tournament_by_id(self, tournament_id):
        try:
            tournament_object = get_object_or_404(
                Tournament, tournament_id=tournament_id
            )
            return tournament_object
        except Tournament.DoesNotExist:
            return None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("PONG CONSUMER INITIALISED")

    async def connect(self):
        # init tournament if not initialized yet
        if self.__class__.tournament is None:
            tournament_id = self.scope["url_route"]["kwargs"]["tournament_id"]
            # init tournament to new instance of Tournament class
            self.__class__.tournament = await self.get_tournament_by_id(tournament_id)

        # accept connection
        await self.accept()
        # close if tournament is over
        if self.__class__.tournament.state == "FINISHED":
            print(
                "User is not authenticated or the tournament is finished, disconnecting"
            )
            await self.close(code=4005)
        # close if not authenticated
        if not (self.scope["user"].is_authenticated):
            print(
                "User is not authenticated or the tournament is finished, disconnecting"
            )
            await self.close(code=4004)
        # add consumer to group
        self.pong_group_name = (
            "tournament_group"  # Define a group name for ping pong game
        )
        await self.channel_layer.group_add(self.pong_group_name, self.channel_name)

        # not sure if this bot handling is needed here
        is_bot = self.scope["query_string"].decode().split("=")[1] == "True"
        if is_bot:
            user = {"id": 0, "username": "ai_bot"}
        else:
            user = self.scope["user"]
        # add player to tournament if eligible
        self.__class__.tournament.connect_player_if_applicable(user)
        self.__class__.tournament.start_tournament_if_applicable()

    async def disconnect(self, close_code):
        # set player status to false in tournament
        await self.__class__.tournament.disconnect_player(self.scope["user"])
        # remove consumer from group
        await self.channel_layer.group_discard(self.pong_group_name, self.channel_name)

    async def handle_game_message(self, message):
        self.__class__.tournament.handle_key_action(
            self.scope["user"], message["key"], message["keyAction"]
        )

    @classmethod
    async def send_game_state_to_all(game_state):
        channel_layer = get_channel_layer()
        try:
            await channel_layer.group_send(
                "tournament_group",
                {
                    "type": "send_game_state",
                    "game_state": game_state,
                },
            )
        except Exception as e:
            print(f"Error sending game state: {e}")

    async def send_game_state(self, event):
        game_state = event["game_state"]
        try:
            await self.send(text_data=json.dumps(game_state))
        except Exception as e:
            print(f"Error sending game state: {e}")

    async def receive(self, text_data):
        if self.__class__.tournament.includes_player(self.scope["user"]):
            try:
                text_data_json = json.loads(text_data)
                message = text_data_json["message"]
                message_type = text_data_json["type"]
                if message_type == "tournament":
                    await self.handle_tournament_message(message)
                elif message_type == "game":
                    await self.handle_game_message(message)
            except Exception as e:
                print("Error in receive method: %s", e)
