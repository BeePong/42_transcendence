import json
import math
import random
import threading
import time
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings

# from django.contrib.auth.models import User

from .models import Match
from django.shortcuts import get_object_or_404
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from .game_state import GameState
from asgiref.sync import sync_to_async
import logging

logger = logging.getLogger(__name__)


class GameLoop:

    def __init__(self, match, tournament_id):
        logger.info("Game loop initializing")
        self.match = match
        self.tournament_id = tournament_id
        self.game_state = GameState(match, tournament_id)
        self.pong_group_name = f"group_{self.tournament_id}"
        self.running = False
        self.loop_task = None
        self.channel_layer = get_channel_layer()
        self.ball_new_x = 100
        self.ball_new_y = 100

    @database_sync_to_async
    def set_state(self, state):
        self.game_state.state = state
        self.match.state = state
        self.match.save()

    async def loop(self):
        logger.info("Game loop started")
        self.running = True
        await self.set_state("COUNTDOWN")
        if not self.loop_task or self.loop_task.done():
            self.loop_task = asyncio.create_task(self.game_loop())

    # define move_paddles

    @sync_to_async
    def handle_key_press(self, message, player_number):
        try:
            
            logger.info(f"Handling key press from {player_number}")
            if message["key"] == "ArrowUp":
                if player_number == 1:
                    self.game_state.player1.up_pressed = True
                elif player_number == 2:
                    self.game_state.player2.up_pressed = True
            elif message["key"] == "ArrowDown":
                if player_number == 1:
                    self.game_state.player1.down_pressed = True
                elif player_number == 2:
                    self.game_state.player2.down_pressed = True
        except Exception as e:
            logger.error(f"Error handling key press: {e}")

    async def handle_countdown(self):
        try:
            if time.time() - self.game_state.round_start_time <= 3:
                logger.info(f"Countdown: {3 - int(time.time() - self.game_state.round_start_time)}")
                self.game_state.countdown = 3 - int(
                    time.time() - self.game_state.round_start_time
                )
            else:
                logger.info("Countdown finished, setting state to PLAYING")
                self.game_state.countdown = 0
                await self.set_state("PLAYING")
        except Exception as e:
            logger.error(f"Error handling countdown: {e}")

    """ async def send_message(self, event):
        message = event["message"]
        type = event["message_type"]
        try:
            text_data = await sync_to_async(json.dumps)(
                {"type": type, "message": message}
            )
            await self.send(text_data=text_data)
        except Exception as e:
            logger.error(f"Error sending message: {e}") """

    async def send_message_to_all(self, message, message_type):
        logger.info(f"Sending message to group_name from game loop: {self.pong_group_name}")

        try:
            await self.channel_layer.group_send(
                self.pong_group_name,
                {
                    "type": "send_message",
                    "message": message,
                    "message_type": message_type,
                },
            )
        except Exception as e:
            logger.error(f"Error sending message to all: {e}")

    async def send_game_state_to_all(self):
        await self.send_message_to_all(self.game_state.to_dict(), "game")

    def move_paddles(self):
        try:
            # Update the position of the paddles based on the key states
            if self.game_state.player1.up_pressed:
                new_y = self.game_state.player1.y - settings.PADDLE_SPEED
                if new_y < settings.UPPER_LIMIT:
                    self.game_state.player1.y = settings.UPPER_LIMIT
                else:
                    self.game_state.player1.y = new_y
                logger.info(f"player1.up_pressed, new y player 1 paddle: {self.game_state.player1.y}")
            elif self.game_state.player1.down_pressed:
                new_y = self.game_state.player1.y + settings.PADDLE_SPEED
                if new_y > settings.LOWER_LIMIT:
                    self.game_state.player1.y = settings.LOWER_LIMIT
                else:
                    self.game_state.player1.y = new_y
                logger.info(f"player1.down_pressed, new y player 1 paddle: {self.game_state.player1.y}")

            if self.game_state.player2.up_pressed:
                new_y = self.game_state.player2.y - settings.PADDLE_SPEED
                if new_y < settings.UPPER_LIMIT:
                    self.game_state.player2.y = settings.UPPER_LIMIT
                else:
                    self.game_state.player2.y = new_y
                logger.info(f"player2.up_pressed, new y player 2 paddle: {self.game_state.player2.y}")
            elif self.game_state.player2.down_pressed:
                new_y = self.game_state.player2.y + settings.PADDLE_SPEED
                if new_y > settings.LOWER_LIMIT:
                    self.game_state.player2.y = settings.LOWER_LIMIT
                else:
                    self.game_state.player2.y = new_y
                logger.info(f"player2.down_pressed, new y player 2 paddle: {self.game_state.player2.y}")
        except Exception as e:
            logger.error(f"Error moving paddles: {e}")

    def calculate_new_ball_position(self):
        logger.info("Calculating new ball position")
        try:
            self.ball_new_x = (
                self.game_state.ball.x
                + self.game_state.ball_speed * self.game_state.ball_vector["x"]
            )
            self.ball_new_y = (
                self.game_state.ball.y
                + self.game_state.ball_speed * self.game_state.ball_vector["y"]
            )
        except Exception as e:
            logger.error(f"Error calculating new ball position: {e}")
        logger.info("calculated new ball position")

    def calculate_collisions(self):
        logger.info("Calculating collisions")
        try:
            # top border
            if self.ball_new_y <= settings.THICK_BORDER_THICKNESS + settings.BALL_RADIUS:
                remaining_movement = (
                    settings.THICK_BORDER_THICKNESS
                    + settings.BALL_RADIUS
                    - self.game_state.ball.y
                )
                self.game_state.ball_vector["y"] *= -1

                self.ball_new_y = (
                    self.game_state.ball.y
                    + remaining_movement * self.game_state.ball_vector["y"]
                )
            # bottom border
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
                self.game_state.ball_vector["y"] *= -1
                self.ball_new_y = (
                    self.game_state.ball.y
                    - remaining_movement * self.game_state.ball_vector["y"]
                )
            logger.info("middle of calculate_collisions")
            # left paddle
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
                logger.info("HIT LEFT PADDLE")
                self.game_state.hit_count += 1
                self.game_state.ball_speed += settings.BALL_SPEED_INCREMENT
                remaining_movement = (
                    settings.PADDING_THICKNESS
                    + settings.PADDLE_WIDTH
                    + settings.BALL_RADIUS
                    - self.game_state.ball.x
                )
                if self.game_state.ball_vector["x"] < 0:
                    self.game_state.ball_vector["x"] *= -1
                    ball_new_x = (
                        self.game_state.ball.x
                        + remaining_movement * self.game_state.ball_vector["x"]
                    )
            # right paddle
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
                logger.info("HIT RIGHT PADDLE")
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
                if self.game_state.ball_vector["x"] > 0:
                    self.game_state.ball_vector["x"] *= -1
                    ball_new_x = (
                        self.game_state.ball.x
                        - remaining_movement * self.game_state.ball_vector["x"]
                    )
        except Exception as e:
            logger.error(f"Error calculating collisions: {e}")

    def get_winner_if_someone_scored(self):
        try:
            if self.ball_new_x >= settings.FIELD_WIDTH - settings.BALL_RADIUS:
                return self.match.player1
            elif self.ball_new_x <= settings.BALL_RADIUS:
                return self.match.player2
            return None
        except Exception as e:
            logger.error(f"Error getting winner if someone scored: {e}")

    @database_sync_to_async
    def check_win(self):
        try:
            logger.info("Checking for winner")
            winner = self.get_winner_if_someone_scored()
            if winner:
                logger.info("we have a winner")
                logger.info(f"Winner: {winner}")
                self.match.winner = winner
                self.match.state = "FINISHED"
                self.game_state.state = "FINISHED"
                self.running = False
                self.match.save()
        except Exception as e:
            logger.error(f"Error checking for winner: {e}")

    async def game_loop(self):

        logger.info("Game loop started")
        while self.running:
            try:
            # paddles move always, even on countdown
                await sync_to_async(self.move_paddles)()
                if self.game_state.state == "COUNTDOWN":
                    await self.handle_countdown()
                elif self.game_state.state == "PLAYING":
                    logger.info("Game loop state PLAYING")
                    await sync_to_async(self.calculate_new_ball_position)()
                    logger.info(f"Ball new x: {self.ball_new_x}, ball new y: {self.ball_new_y}")
                    await sync_to_async(self.calculate_collisions)()
                    logger.info(f"After collision: Ball new x: {self.ball_new_x}, ball new y: {self.ball_new_y}")
                    self.game_state.ball.x = self.ball_new_x
                    self.game_state.ball.y = self.ball_new_y
                    await self.check_win()
                await self.send_game_state_to_all()
                if self.game_state.state == "FINISHED":
                    logger.info("Game finished")
                    # should we send tournament message instead? or nothing?
                    await self.send_game_state_to_all()
                await asyncio.sleep(1 / settings.FPS)
            except Exception as e:
                logger.error(f"Error in game loop: {e}")
        logger.info("Game loop finished")

    def stop(self):
        logger.info("Game loop stopped")
        self.running = False
        if self.loop_task:
            self.loop_task.cancel()
            self.loop_task = None