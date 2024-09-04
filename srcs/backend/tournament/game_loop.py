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
from .consumers import PongConsumer
from .game_state import GameState


class GameLoop:

    def __init__(self, match, tournament_id, game_state):
        print("INIT GAME LOOP, match id: ", match.game_id)
        self.match = match
        self.tournament_id = tournament_id
        self.game_state = game_state
        self.pong_group_name = f"group_{self.tournament_id}"
        self.running = True
        self.loop_task = None
        self.channel_layer = get_channel_layer()
        print("GAME LOOP INITIALIZED, match id: ", self.match.game_id)

    async def loop(self):
        if not self.loop_task or self.loop_task.done():
            self.loop_task = asyncio.create_task(self.game_loop())

    # define move_paddles

    def handle_countdown(self):
        if time.time() - self.game_state.round_start_time <= 3:
            self.game_state.countdown = 3 - int(
                time.time() - self.game_state.round_start_time
            )
        else:
            self.game_state.countdown = 0
            self.game_state.state = "PLAYING"
            print("state changed to PLAYING")
            self.match.state = "PLAYING"
            self.match.save()

    def move_paddles(self):
        # Update the position of the paddles based on the key states
        if self.game_state.player1.up_pressed:
            new_y = self.game_state.player1.y - settings.PADDLE_SPEED
            if new_y < settings.UPPER_LIMIT:
                self.game_state.player1.y = settings.UPPER_LIMIT
            else:
                self.game_state.player1.y = new_y
            print("new y player 1 paddle: ", self.game_state.player1.y)
        elif self.game_state.player1.down_pressed:
            new_y = self.game_state.player1.y + settings.PADDLE_SPEED
            if new_y > settings.LOWER_LIMIT:
                self.game_state.player1.y = settings.LOWER_LIMIT
            else:
                self.game_state.player1.y = new_y
            print("new y player 1 paddle: ", self.game_state.player1.y)

        if self.game_state.player2.up_pressed:
            new_y = self.game_state.player2.y - settings.PADDLE_SPEED
            if new_y < settings.UPPER_LIMIT:
                self.game_state.player2.y = settings.UPPER_LIMIT
            else:
                self.game_state.player2.y = new_y
            print("new y player 2 paddle: ", self.game_state.player2.y)
        elif self.game_state.player2.down_pressed:
            new_y = self.game_state.player2.y + settings.PADDLE_SPEED
            if new_y > settings.LOWER_LIMIT:
                self.game_state.player2.y = settings.LOWER_LIMIT
            else:
                self.game_state.player2.y = new_y
            print("new y player 2 paddle: ", self.game_state.player2.y)

    def calculate_new_ball_position(self):
        self.ball_new_x = (
            self.game_state.ball.x
            + self.game_state.ball_speed * self.game_state.ball_vector.x
        )
        self.ball_new_y = (
            self.game_state.ball.y
            + self.game_state.ball_speed * self.game_state.ball_vector.y
        )

    def calculate_collisions(self):
        if self.ball_new_y <= settings.THICK_BORDER_THICKNESS + settings.BALL_RADIUS:
            remaining_movement = (
                settings.THICK_BORDER_THICKNESS
                + settings.BALL_RADIUS
                - self.game_state.ball.y
            )
            self.game_state.ball_vector.y *= -1

            self.ball_new_y = (
                self.game_state.ball.y
                + remaining_movement * self.game_state.ball_vector.y
            )
        elif (
            self.ball_new_y
            >= settings.FIELD_HEIGHT
            - settings.THICK_BORDER_THICKNESS
            - settings.BALL_RADIUS
        ):
            remaining_movement = (
                self.game_state.ball.y
                + settings.BALL_RADIUS
                - (settings.FIELD_HEIGHT - settings.THICK_BORDER_THICKNESS)
            )
            self.game_state.ball_vector.y *= -1
            self.ball_new_y = (
                self.game_state.ball.y
                - remaining_movement * self.game_state.ball_vector.y
            )
        if (
            self.ball_new_x
            < settings.PADDING_THICKNESS + settings.PADDLE_WIDTH + settings.BALL_RADIUS
            and self.game_state.player2.y
            - settings.PADDLE_HEIGHT / 2
            - settings.BALL_RADIUS
            <= self.ball_new_y
            <= self.game_state.player2.y
            + settings.PADDLE_HEIGHT / 2
            + settings.BALL_RADIUS
        ):
            print("HIT LEFT PADDLE")
            self.game_state.hit_count += 1
            self.game_state.ball_speed += settings.BALL_SPEED_INCREMENT
            remaining_movement = (
                settings.PADDING_THICKNESS
                + settings.PADDLE_WIDTH
                + settings.BALL_RADIUS
                - self.game_state.ball.x
            )
            if self.game_state.ball_vector.x < 0:
                self.game_state.ball_vector.x *= -1
                ball_new_x = (
                    self.game_state.ball.x
                    + remaining_movement * self.game_state.ball_vector.x
                )
            elif (
                ball_new_x
                > settings.FIELD_WIDTH
                - settings.PADDING_THICKNESS
                - settings.PADDLE_WIDTH
                - settings.BALL_RADIUS
                and self.game_state.player1.y
                - settings.PADDLE_HEIGHT / 2
                - settings.BALL_RADIUS
                <= self.ball_new_y
                <= self.game_state.player1.y
                + settings.PADDLE_HEIGHT / 2
                + settings.BALL_RADIUS
            ):
                print("HIT RIGHT PADDLE")
                self.game_state.hit_count += 1
                self.game_state.ball_speed += settings.BALL_SPEED_INCREMENT
                remaining_movement = (
                    self.game_state.ball.x
                    + settings.BALL_RADIUS
                    - (
                        settings.FIELD_WIDTH
                        - settings.PADDING_THICKNESS
                        - settings.PADDLE_WIDTH
                    )
                )
                if self.game_state.ball_vector.x > 0:
                    self.game_state.ball_vector.x *= -1
                    ball_new_x = (
                        self.game_state.ball.x
                        - remaining_movement * self.game_state.ball_vector.x
                    )

    def check_win(self):
        if self.ball_new_x >= settings.FIELD_WIDTH - settings.BALL_RADIUS:
            print("PLAYER 1 SCORED")
            self.match.winner = self.match.player1
            self.match.state = "FINISHED"
            self.running = False
            self.match.save()
        elif self.ball_new_x <= settings.BALL_RADIUS:
            print("PLAYER 2 SCORED")
            self.match.winner = self.match.player2
            self.match.state = "FINISHED"
            self.running = False
            self.match.save()

    async def game_loop(self):

        print("GAME LOOP STARTED")
        while self.running:
            # paddles move always, even on countdown
            self.move_paddles()
            if self.match.state == "COUNTDOWN":
                self.handle_countdown()
            elif self.match.state == "PLAYING":
                self.calculate_new_ball_position()
                self.calculate_collisions()
                self.game_state.ball.x = self.ball_new_x
                self.game_state.ball.y = self.ball_new_y
                self.check_win()
            await self.send_game_state_to_all(self.game_state)

            if self.match.state == "FINISHED":
                print("MATCH FINISHED")
                # self.send_tournament_state_to_all()
            await asyncio.sleep(1 / settings.FPS)

    def stop(self):
        print("STOP GAME LOOP")
        self.running = False
        if self.loop_task:
            self.loop_task.cancel()
            self.loop_task = None
