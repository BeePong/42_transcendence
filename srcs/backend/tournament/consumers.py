import json
import time
import threading
import random
import math
from channels.generic.websocket import WebsocketConsumer
from enum import Enum
from django.conf import settings

# import asyncio
# from .ai import ai_bot


class GameState(Enum):
    COUNTDOWN = "countdown"
    PLAYING = "playing"
    FINISHED = "finished"


def get_larger_random():
    y = 0
    while abs(y) < 0.2:
        y = random.uniform(-1, 1)
    return y


def normalize_vector(x, y):
    magnitude = math.sqrt(x**2 + y**2)
    return {"x": x / magnitude, "y": y / magnitude}


game_state = {
    "round_start_time": time.time(),
    "state": GameState.COUNTDOWN.value,
    "countdown": 3,
    "ball": {"x": settings.FIELD_WIDTH / 2, "y": settings.FIELD_HEIGHT / 2},
    "ball_speed": 10,
    "hit_count": 0,
    "ball_vector": normalize_vector(get_larger_random(), random.uniform(-1, 1)),
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


def init_new_round(game_state):
    game_state["round_start_time"] = time.time()
    game_state["state"] = GameState.COUNTDOWN.value
    game_state["countdown"] = 3
    game_state["hit_count"] = 0
    game_state["ball"] = {"x": settings.FIELD_WIDTH / 2, "y": settings.FIELD_HEIGHT / 2}
    game_state["ball_vector"] = normalize_vector(
        get_larger_random(), random.uniform(-1, 1)
    )
    # print("NEW ROUND INITIALIZED")


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
        self.thread = threading.Thread(target=self.loop)

    def start(self):
        self.thread.start()

    def loop(self):
        self.game_loop()

    def game_loop(self):
        # Your game loop code here, which can use self.game_state
        while True:
            time.sleep(1 / settings.FPS)
            if self.game_state["state"] == GameState.COUNTDOWN.value:
                if time.time() - self.game_state["round_start_time"] <= 3:
                    self.game_state["countdown"] = 3 - int(
                        time.time() - self.game_state["round_start_time"]
                    )
                else:
                    self.game_state["countdown"] = 0
                    self.game_state["state"] = GameState.PLAYING.value
            elif self.game_state["state"] == GameState.PLAYING.value:
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

                # instead of left paddle place another wall for debugging
                # handle collisions with left wall
                # if ball_new_x <= self.BALL_RADIUS:
                # Calculate the remaining movement after the ball hits the wall
                # remaining_movement = self.BALL_RADIUS - self.game_state['ball']['x']
                # Reverse the x-component of the ball's direction vector
                # self.game_state['ball_vector']['x'] *= -1
                # Move the ball the remaining distance in the new direction
                # ball_new_x = self.game_state['ball']['x'] + remaining_movement * self.game_state['ball_vector']['x']

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
                    self.game_state["hit_count"] += 1
                    # Calculate the remaining movement after the ball hits the wall
                    remaining_movement = (
                        settings.PADDING_THICKNESS
                        + settings.PADDLE_WIDTH
                        - self.game_state["ball"]["x"]
                    )
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
                    self.game_state["player1"]["score"] += 1
                    init_new_round(game_state)
                    if self.game_state["player1"]["score"] == settings.MAX_SCORE:
                        self.game_state["winner"] = self.game_state["player1"][
                            "player_id"
                        ]
                        self.game_state["state"] = GameState.COUNTDOWN.value
                        self.game_state["player2"]["score"] = 0
                        self.game_state["player1"]["score"] = 0
                elif ball_new_x <= settings.BALL_RADIUS:
                    self.game_state["player2"]["score"] += 1
                    init_new_round(game_state)
                    if self.game_state["player2"]["score"] == settings.MAX_SCORE:
                        self.game_state["winner"] = self.game_state["player2"][
                            "player_id"
                        ]
                        self.game_state["state"] = GameState.COUNTDOWN.value
                        self.game_state["player2"]["score"] = 0
                        self.game_state["player1"]["score"] = 0
            PongConsumer.send_game_state_to_all()


class PongConsumer(WebsocketConsumer):

    consumers = []

    game_loop = GameLoop.get_instance(game_state)
    game_thread = threading.Thread(target=game_loop.loop)
    game_thread.start()
    print("GAME THREAD STARTED")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__class__.consumers.append(self)
        print("CONSUMERS: ", self.__class__.consumers)

    def get_player_by_user(self, user):
        if user.username == game_state["player1"]["player_name"]:
            return "player1"
        elif user.username == game_state["player2"]["player_name"]:
            return "player2"
        else:
            return None

    def send_message(self, message):
        self.send(text_data=json.dumps({"message": message}))

    def connect(self):
        print("Attempting to connect...")
        self.accept()
        print("Connection accepted")
        is_bot = self.scope["query_string"].decode().split("=")[1] == "True"
        if is_bot:
            user = {"id": 0, "username": "ai_bot"}
        else:
            user = self.scope["user"]
        # TODO: change this to the actual player id, now latest person who joins is the main player, the other one is dummy
        player = self.get_player_by_user(user)
        if not player is None:
            game_state[player]["player_id"] = user.id
            print("PLAYER CONNECTED: ", player, user)
        print("USER CONNECTED: ", user)
        if player is None:
            print("User is not playing this game, they are a viewer")
        if self.scope["user"].is_authenticated:
            print("authenticated user id: ", self.scope["user"].id)
            print("authenticated user name: ", self.scope["user"].username)
        print("GAME STATE: ", game_state)

    def disconnect(self, close_code):
        self.__class__.consumers.remove(self)

    def handle_tournament_message(self, message):
        self.send_message("Received tournament message: " + str(message))

    def handle_key_event(self, key, keyAction, player_field):
        if key == "ArrowUp":
            game_state[player_field]["up_pressed"] = keyAction == "keydown"
        elif key == "ArrowDown":
            game_state[player_field]["down_pressed"] = keyAction == "keydown"

    def handle_game_message(self, message):
        player = self.scope["user"]
        key = message["key"]
        keyAction = message["keyAction"]
        # Update the game state based on the key and action
        if player.id == game_state["player1"]["player_id"]:
            self.handle_key_event(key, keyAction, "player1")
        elif player.id == game_state["player2"]["player_id"]:
            self.handle_key_event(key, keyAction, "player2")

    def send_game_state(self):
        # Send the updated game state to all players
        self.send(text_data=json.dumps(game_state))

    @classmethod
    def send_game_state_to_all(cls):
        # print("SENDING GAME STATE TO ALL")
        for consumer in cls.consumers:
            consumer.send_game_state()

    def receive(self, text_data):
        # TODO: only receive data from users who are playing the current game, ignore everyone else - it's done in handle_game_message function now, but this function would be a better place for this
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        message_type = text_data_json["type"]

        if message_type == "tournament":
            self.handle_tournament_message(message)
        elif message_type == "game":
            self.handle_game_message(message)
