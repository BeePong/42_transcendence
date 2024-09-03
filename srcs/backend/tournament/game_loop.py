# import json
# import math
# import random
# import threading
# import time
# import asyncio
# from channels.generic.websocket import AsyncWebsocketConsumer
# from enum import Enum
# from django.conf import settings

# # from django.contrib.auth.models import User

# from .models import Tournament, Player
# from django.shortcuts import get_object_or_404
# from channels.db import database_sync_to_async
# from channels.layers import get_channel_layer
# from .consumers import PongConsumer

# class GameState(Enum):
#     COUNTDOWN = "countdown"
#     PLAYING = "playing"
#     FINISHED = "finished"


# class GameLoop:

#     _instance = None

#     @classmethod
#     def get_instance(cls, game_state):
#         if cls._instance is None:
#             cls._instance = cls(game_state)
#             cls._instance.start()
#         return cls._instance

#     def __init__(self, game_state):
#         self.game_state = game_state
#         self.running = True
#         self.loop_task = None
#         print("GAME LOOP INITIALIZED")

#     def start(self):
#         self.loop_task = asyncio.create_task(self.game_loop())

#     async def loop(self):
#         self.loop_task = asyncio.create_task(self.game_loop())

#     async def game_loop(self):
#         print("GAME LOOP STARTED")
#         # Your game loop code here, which can use self.game_state
#         while self.running:
#             if self.game_state["state"] == GameState.COUNTDOWN.value:
#                 if time.time() - self.game_state["round_start_time"] <= 3:
#                     self.game_state["countdown"] = 3 - int(
#                         time.time() - self.game_state["round_start_time"]
#                     )
#                 else:
#                     self.game_state["countdown"] = 0
#                     self.game_state["state"] = GameState.PLAYING.value

#             # Update the position of the paddles based on the key states
#             for player_id in ["player1", "player2"]:
#                 if self.game_state[player_id]["up_pressed"]:
#                     new_y = self.game_state[player_id]["y"] - settings.PADDLE_SPEED
#                     if new_y < settings.UPPER_LIMIT:
#                         self.game_state[player_id]["y"] = settings.UPPER_LIMIT
#                     else:
#                         self.game_state[player_id]["y"] = new_y

#                 elif self.game_state[player_id]["down_pressed"]:
#                     new_y = self.game_state[player_id]["y"] + settings.PADDLE_SPEED
#                     if new_y > settings.LOWER_LIMIT:
#                         self.game_state[player_id]["y"] = settings.LOWER_LIMIT
#                     else:
#                         self.game_state[player_id]["y"] = new_y

#             if self.game_state["state"] == GameState.PLAYING.value:
#                 # Calculate next position of the ball
#                 ball_new_x = (
#                     self.game_state["ball"]["x"]
#                     + self.game_state["ball_speed"]
#                     * self.game_state["ball_vector"]["x"]
#                 )
#                 ball_new_y = (
#                     self.game_state["ball"]["y"]
#                     + self.game_state["ball_speed"]
#                     * self.game_state["ball_vector"]["y"]
#                 )

#                 # Check for collisions with the game boundaries
#                 if ball_new_y <= settings.THICK_BORDER_THICKNESS + settings.BALL_RADIUS:
#                     # Calculate the remaining movement after the ball hits the wall
#                     remaining_movement = (
#                         settings.THICK_BORDER_THICKNESS
#                         + settings.BALL_RADIUS
#                         - self.game_state["ball"]["y"]
#                     )
#                     # Reverse the y-component of the ball's direction vector
#                     self.game_state["ball_vector"]["y"] *= -1
#                     # Move the ball the remaining distance in the new direction
#                     ball_new_y = (
#                         self.game_state["ball"]["y"]
#                         + remaining_movement * self.game_state["ball_vector"]["y"]
#                     )
#                 elif (
#                     ball_new_y
#                     >= settings.FIELD_HEIGHT
#                     - settings.THICK_BORDER_THICKNESS
#                     - settings.BALL_RADIUS
#                 ):
#                     # Calculate the remaining movement after the ball hits the wall
#                     remaining_movement = (
#                         self.game_state["ball"]["y"]
#                         + settings.BALL_RADIUS
#                         - (settings.FIELD_HEIGHT - settings.THICK_BORDER_THICKNESS)
#                     )
#                     # Reverse the y-component of the ball's direction vector
#                     self.game_state["ball_vector"]["y"] *= -1
#                     # Move the ball the remaining distance in the new direction
#                     ball_new_y = (
#                         self.game_state["ball"]["y"]
#                         - remaining_movement * self.game_state["ball_vector"]["y"]
#                     )

#                 # Collisions with the paddles
#                 if (
#                     ball_new_x
#                     < settings.PADDING_THICKNESS
#                     + settings.PADDLE_WIDTH
#                     + settings.BALL_RADIUS
#                     and self.game_state["player2"]["y"]
#                     - settings.PADDLE_HEIGHT / 2
#                     - settings.BALL_RADIUS
#                     <= ball_new_y
#                     <= self.game_state["player2"]["y"]
#                     + settings.PADDLE_HEIGHT / 2
#                     + settings.BALL_RADIUS
#                 ):
#                     # print("HIT LEFT PADDLE")
#                     self.game_state["hit_count"] += 1
#                     self.game_state["ball_speed"] += settings.BALL_SPEED_INCREMENT
#                     # Calculate the remaining movement after the ball hits the wall
#                     remaining_movement = (
#                         settings.PADDING_THICKNESS
#                         + settings.PADDLE_WIDTH
#                         + settings.BALL_RADIUS
#                         - self.game_state["ball"]["x"]
#                     )
#                     # check if ball is moving towards the paddle
#                     if self.game_state["ball_vector"]["x"] < 0:
#                         # Reverse the x-component of the ball's direction vector
#                         self.game_state["ball_vector"]["x"] *= -1
#                         # Move the ball the remaining distance in the new direction
#                         ball_new_x = (
#                             self.game_state["ball"]["x"]
#                             + remaining_movement * self.game_state["ball_vector"]["x"]
#                         )
#                 if (
#                     ball_new_x
#                     > settings.FIELD_WIDTH
#                     - settings.PADDING_THICKNESS
#                     - settings.PADDLE_WIDTH
#                     - settings.BALL_RADIUS
#                     and self.game_state["player1"]["y"]
#                     - settings.PADDLE_HEIGHT / 2
#                     - settings.BALL_RADIUS
#                     <= ball_new_y
#                     <= self.game_state["player1"]["y"]
#                     + settings.PADDLE_HEIGHT / 2
#                     + settings.BALL_RADIUS
#                 ):
#                     self.game_state["hit_count"] += 1
#                     self.game_state["ball_speed"] += settings.BALL_SPEED_INCREMENT
#                     # Calculate the remaining movement after the ball hits the wall
#                     remaining_movement = (
#                         self.game_state["ball"]["x"]
#                         + settings.BALL_RADIUS
#                         - (
#                             settings.FIELD_WIDTH
#                             - settings.PADDING_THICKNESS
#                             - settings.PADDLE_WIDTH
#                         )
#                     )
#                     # check  if ball is moving towards the paddle
#                     if self.game_state["ball_vector"]["x"] > 0:
#                         # Reverse the x-component of the ball's direction vector
#                         self.game_state["ball_vector"]["x"] *= -1
#                         # Move the ball the remaining distance in the new direction
#                         ball_new_x = (
#                             self.game_state["ball"]["x"]
#                             - remaining_movement * self.game_state["ball_vector"]["x"]
#                         )

#                 # Update the ball's position
#                 self.game_state["ball"]["x"] = ball_new_x
#                 self.game_state["ball"]["y"] = ball_new_y

#                 # Check for scoring
#                 if ball_new_x >= settings.FIELD_WIDTH - settings.BALL_RADIUS:
#                     print("PLAYER 1 SCORED")
#                     self.game_state["player1"]["score"] += 1
#                     GameStateSingleton.get_instance().init_new_round()
#                     if self.game_state["player1"]["score"] == settings.MAX_SCORE:
#                         self.game_state["winner"] = self.game_state["player1"][
#                             "player_id"
#                         ]
#                         self.game_state["state"] = GameState.FINISHED.value
#                         self.game_state["player2"]["score"] = 0
#                         self.game_state["player1"]["score"] = 0
#                 elif ball_new_x <= settings.BALL_RADIUS:
#                     print("PLAYER 2 SCORED")
#                     self.game_state["player2"]["score"] += 1
#                     GameStateSingleton.get_instance().init_new_round()
#                     if self.game_state["player2"]["score"] == settings.MAX_SCORE:
#                         self.game_state["winner"] = self.game_state["player2"][
#                             "player_id"
#                         ]
#                         self.game_state["state"] = GameState.FINISHED.value
#                         self.game_state["player2"]["score"] = 0
#                         self.game_state["player1"]["score"] = 0

#             await PongConsumer.send_game_state_to_all()
#             await asyncio.sleep(1 / settings.FPS)

#     def stop(self):
#         self.running = False
#         if self.loop_task:
#             self.loop_task.cancel()
