import json
import asyncio
import time
import random
import math
from channels.generic.websocket import AsyncWebsocketConsumer
from enum import Enum
from django.conf import settings
from .models import Tournament, Player
from django.shortcuts import get_object_or_404
from channels.db import database_sync_to_async
from asgiref.sync import async_to_sync
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



class GameStateSingleton:
    _instance = None

    def get_larger_random(self):
        y = 0
        while abs(y) < 0.2:
            y = random.uniform(-1, 1)
        return y

    def normalize_vector(self, x, y):
        magnitude = math.sqrt(x**2 + y**2)
        return {"x": x / magnitude, "y": y / magnitude}

    def __init__(self):
        self.__class__._instance = self
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

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

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
        self.game_state["player1"]["score"] = 0
        self.game_state["player1"]["player_id"] = None
        self.game_state["player2"]["score"] = 0
        self.game_state["player2"]["player_id"] = None
        self.game_state["winner"] = None


class GameLoop:

    _instance = None

    @classmethod
    def get_instance(cls, game_state):
        if cls._instance is None:
            cls._instance = cls(game_state)
            cls._instance.start()
        return cls._instance

    def __init__(self, game_state):
        self.game_state = game_state
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
            if self.game_state["state"] == GameState.COUNTDOWN.value:
                if time.time() - self.game_state["round_start_time"] <= 3:
                    self.game_state["countdown"] = 3 - int(
                        time.time() - self.game_state["round_start_time"]
                    )
                else:
                    self.game_state["countdown"] = 0
                    self.game_state["state"] = GameState.PLAYING.value

            # Update the position of the paddles based on the key states
            for player_id in ["player1", "player2"]:
                if self.game_state[player_id]["up_pressed"]:
                    new_y = self.game_state[player_id]["y"] - settings.PADDLE_SPEED
                    if new_y < settings.UPPER_LIMIT:
                        self.game_state[player_id]["y"] = settings.UPPER_LIMIT
                    else:
                        self.game_state[player_id]["y"] = new_y

                elif self.game_state[player_id]["down_pressed"]:
                    new_y = self.game_state[player_id]["y"] + settings.PADDLE_SPEED
                    if new_y > settings.LOWER_LIMIT:
                        self.game_state[player_id]["y"] = settings.LOWER_LIMIT
                    else:
                        self.game_state[player_id]["y"] = new_y

            if self.game_state["state"] == GameState.PLAYING.value:
                # Calculate next position of the ball
                ball_new_x = (
                    self.game_state["ball"]["x"]
                    + self.game_state["ball_speed"]
                    * self.game_state["ball_vector"]["x"]
                )
                ball_new_y = (
                    self.game_state["ball"]["y"]
                    + self.game_state["ball_speed"]
                    * self.game_state["ball_vector"]["y"]
                )

                # Check for collisions with the game boundaries
                if ball_new_y <= settings.THICK_BORDER_THICKNESS + settings.BALL_RADIUS:
                    # Calculate the remaining movement after the ball hits the wall
                    remaining_movement = (
                        settings.THICK_BORDER_THICKNESS
                        + settings.BALL_RADIUS
                        - self.game_state["ball"]["y"]
                    )
                    # Reverse the y-component of the ball's direction vector
                    self.game_state["ball_vector"]["y"] *= -1
                    # Move the ball the remaining distance in the new direction
                    ball_new_y = (
                        self.game_state["ball"]["y"]
                        + remaining_movement * self.game_state["ball_vector"]["y"]
                    )
                elif (
                    ball_new_y
                    >= settings.FIELD_HEIGHT
                    - settings.THICK_BORDER_THICKNESS
                    - settings.BALL_RADIUS
                ):
                    # Calculate the remaining movement after the ball hits the wall
                    remaining_movement = (
                        self.game_state["ball"]["y"]
                        + settings.BALL_RADIUS
                        - (settings.FIELD_HEIGHT - settings.THICK_BORDER_THICKNESS)
                    )
                    # Reverse the y-component of the ball's direction vector
                    self.game_state["ball_vector"]["y"] *= -1
                    # Move the ball the remaining distance in the new direction
                    ball_new_y = (
                        self.game_state["ball"]["y"]
                        - remaining_movement * self.game_state["ball_vector"]["y"]
                    )

                # Collisions with the paddles
                if (
                    ball_new_x
                    < settings.PADDING_THICKNESS
                    + settings.PADDLE_WIDTH
                    + settings.BALL_RADIUS
                    and self.game_state["player2"]["y"]
                    - settings.PADDLE_HEIGHT / 2
                    - settings.BALL_RADIUS
                    <= ball_new_y
                    <= self.game_state["player2"]["y"]
                    + settings.PADDLE_HEIGHT / 2
                    + settings.BALL_RADIUS
                ):
                    # print("HIT LEFT PADDLE")
                    self.game_state["hit_count"] += 1
                    self.game_state["ball_speed"] += settings.BALL_SPEED_INCREMENT
                    # Calculate the remaining movement after the ball hits the wall
                    remaining_movement = (
                        settings.PADDING_THICKNESS
                        + settings.PADDLE_WIDTH
                        + settings.BALL_RADIUS
                        - self.game_state["ball"]["x"]
                    )
                    # check if ball is moving towards the paddle
                    if self.game_state["ball_vector"]["x"] < 0:
                        # Reverse the x-component of the ball's direction vector
                        self.game_state["ball_vector"]["x"] *= -1
                        # Move the ball the remaining distance in the new direction
                        ball_new_x = (
                            self.game_state["ball"]["x"]
                            + remaining_movement * self.game_state["ball_vector"]["x"]
                        )
                if (
                    ball_new_x
                    > settings.FIELD_WIDTH
                    - settings.PADDING_THICKNESS
                    - settings.PADDLE_WIDTH
                    - settings.BALL_RADIUS
                    and self.game_state["player1"]["y"]
                    - settings.PADDLE_HEIGHT / 2
                    - settings.BALL_RADIUS
                    <= ball_new_y
                    <= self.game_state["player1"]["y"]
                    + settings.PADDLE_HEIGHT / 2
                    + settings.BALL_RADIUS
                ):
                    self.game_state["hit_count"] += 1
                    self.game_state["ball_speed"] += settings.BALL_SPEED_INCREMENT
                    # Calculate the remaining movement after the ball hits the wall
                    remaining_movement = (
                        self.game_state["ball"]["x"]
                        + settings.BALL_RADIUS
                        - (
                            settings.FIELD_WIDTH
                            - settings.PADDING_THICKNESS
                            - settings.PADDLE_WIDTH
                        )
                    )
                    # check  if ball is moving towards the paddle
                    if self.game_state["ball_vector"]["x"] > 0:
                        # Reverse the x-component of the ball's direction vector
                        self.game_state["ball_vector"]["x"] *= -1
                        # Move the ball the remaining distance in the new direction
                        ball_new_x = (
                            self.game_state["ball"]["x"]
                            - remaining_movement * self.game_state["ball_vector"]["x"]
                        )

                # Update the ball's position
                self.game_state["ball"]["x"] = ball_new_x
                self.game_state["ball"]["y"] = ball_new_y

                # Check for scoring
                if ball_new_x >= settings.FIELD_WIDTH - settings.BALL_RADIUS:
                    print("PLAYER 1 SCORED")
                    self.game_state["player1"]["score"] += 1
                    GameStateSingleton.get_instance().init_new_round()
                    if self.game_state["player1"]["score"] == settings.MAX_SCORE:
                        self.game_state["winner"] = self.game_state["player1"][
                            "player_id"
                        ]
                        self.game_state["state"] = GameState.FINISHED.value
                        self.game_state["player2"]["score"] = 0
                        self.game_state["player1"]["score"] = 0
                elif ball_new_x <= settings.BALL_RADIUS:
                    print("PLAYER 2 SCORED")
                    self.game_state["player2"]["score"] += 1
                    GameStateSingleton.get_instance().init_new_round()
                    if self.game_state["player2"]["score"] == settings.MAX_SCORE:
                        self.game_state["winner"] = self.game_state["player2"][
                            "player_id"
                        ]
                        self.game_state["state"] = GameState.FINISHED.value
                        self.game_state["player2"]["score"] = 0
                        self.game_state["player1"]["score"] = 0

            await PongConsumer.send_game_state_to_all()
            await asyncio.sleep(1 / settings.FPS)

    def stop(self):
        self.running = False
        if self.loop_task:
            self.loop_task.cancel()


class PongConsumer(AsyncWebsocketConsumer):


    game_state = GameStateSingleton.get_instance().game_state
    game_loop = GameLoop(game_state)
    
    print("GAME STARTED")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def get_player_by_user(self, user):
        if user.username == self.__class__.game_state["player1"]["player_name"]:
            return "player1"
        elif user.username == self.__class__.game_state["player2"]["player_name"]:
            return "player2"
        else:
            return None

    async def send_message(self, message):
        await self.send(text_data=json.dumps({"message": message}))

    @database_sync_to_async
    def get_tournament(self, tournament_id):
        try:
            tournament = get_object_or_404(Tournament, tournament_id=tournament_id)
            return tournament
        except Tournament.DoesNotExist:
            return None

    @database_sync_to_async
    def start_tournament(self, tournament):

        tournament.save()

    async def connect(self):
        tournament_id = self.scope["url_route"]["kwargs"]["tournament_id"]
        # Retrieve the tournament object using the tournament_id
        tournament = await self.get_tournament(tournament_id)

        print("TOURNAMENT OBJECT: ", tournament)
        await self.accept()
        self.pong_group_name = (
            "tournament_group"  # Define a group name for ping pong game
        )
        await self.channel_layer.group_add(self.pong_group_name, self.channel_name)

        if not (self.scope["user"].is_authenticated):
            print("User is not authenticated, disconnecting")
            await self.close(code=4004)
        else:
            print("authenticated user id: ", self.scope["user"].id)
            print("authenticated user name: ", self.scope["user"].username)
        is_bot = self.scope["query_string"].decode().split("=")[1] == "True"
        if is_bot:
            user = {"id": 0, "username": "ai_bot"}
        else:
            user = self.scope["user"]
        player = await self.get_player_by_user(user)
        if not player is None:
            self.__class__.game_state[player]["player_id"] = user.id
            print("PLAYER CONNECTED: ", player, user)
        print("USER CONNECTED: ", user)
        if player is None:
            print("User is not playing this game, they are a viewer")
        print("GAME STATE: ", self.__class__.game_state)
        await self.__class__.game_loop.loop()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.pong_group_name, self.channel_name)
        print("CONSUMER DISCONNECTED, close_code: ", close_code)

    async def handle_tournament_message(self, message):
        await self.send_message("Received tournament message: " + str(message))

    async def handle_key_event(self, key, keyAction, player_field):
        if key == "ArrowUp":
            self.__class__.game_state[player_field]["up_pressed"] = (
                keyAction == "keydown"
            )
        elif key == "ArrowDown":
            self.__class__.game_state[player_field]["down_pressed"] = (
                keyAction == "keydown"
            )

    async def handle_game_message(self, message):
        player = self.scope["user"]
        key = message["key"]
        keyAction = message["keyAction"]
        # Update the game state based on the key and action
        if player.id == self.__class__.game_state["player1"]["player_id"]:
            await self.handle_key_event(key, keyAction, "player1")
        elif player.id == self.__class__.game_state["player2"]["player_id"]:
            await self.handle_key_event(key, keyAction, "player2")

    @classmethod
    async def send_game_state_to_all(cls):
        channel_layer = get_channel_layer()
        try:
            await channel_layer.group_send(
                "tournament_group",
                {
                    "type": "send_game_state",
                    "game_state": cls.game_state,
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
        # TODO: only receive data from users who are playing the current game, ignore everyone else - it's done in handle_game_message function now, but this function would maybe be a better place for this
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
