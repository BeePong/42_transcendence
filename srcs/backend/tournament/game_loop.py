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

from .models import Tournament

logger = logging.getLogger(__name__)


class GameLoop:

    def __init__(self, match, tournament_id, tournament):
        logger.info("Game loop initializing")
        self.match = match
        self.tournament_id = tournament_id
        self.tournament = tournament
        self.tournament_countdown = settings.COUNTDOWN_TIME + 1
        self.prev_tournament_countdown = settings.COUNTDOWN_TIME + 2
        self.is_tournament_countdown = False
        self.game_state = GameState(match, tournament_id)
        self.pong_group_name = f"group_{self.tournament_id}"
        self.running = False
        self.loop_task = None
        self.channel_layer = get_channel_layer()
        self.channel_info = None
        self.ball_new_x = 100
        self.ball_new_y = 100

    @database_sync_to_async
    def set_tournament_countdown(self, countdown):
        self.tournament.is_countdown = True
        self.tournament.countdown = countdown
        self.tournament.save()

    @database_sync_to_async
    def set_state(self, state):
        self.game_state.state = state
        self.match.state = state
        self.match.save()

    async def loop(self, channel_info):
        self.channel_info = channel_info
        logger.info(f"{channel_info} Game loop started")
        self.running = True
        await self.set_state("COUNTDOWN")
        if not self.loop_task or self.loop_task.done():
            self.loop_task = asyncio.create_task(self.game_loop())

    # define move_paddles

    @sync_to_async
    def handle_key_press(self, message, player_number):
        try:

            logger.info(f"{self.channel_info} Handling key press from {player_number}")
            is_pressed = message["keyAction"] == "keydown"
            if message["key"] == "ArrowUp":
                if player_number == 1:
                    self.game_state.player1.up_pressed = is_pressed
                elif player_number == 2:
                    self.game_state.player2.up_pressed = is_pressed
            elif message["key"] == "ArrowDown":
                if player_number == 1:
                    self.game_state.player1.down_pressed = is_pressed
                elif player_number == 2:
                    self.game_state.player2.down_pressed = is_pressed
        except Exception as e:
            logger.error(f"{self.channel_info} Error handling key press: {e}")

    async def handle_countdown(self):
        try:
            # tournament countdown
            if (
                time.time() - self.game_state.round_start_time
                <= settings.COUNTDOWN_TIME / 2
            ):
                if not self.is_tournament_countdown:
                    self.is_tournament_countdown = True
                self.prev_tournament_countdown = self.tournament_countdown
                self.tournament_countdown = (
                    settings.COUNTDOWN_TIME
                    - int(time.time() - self.game_state.round_start_time)
                    - settings.COUNTDOWN_TIME / 2
                )
                if self.tournament_countdown != self.prev_tournament_countdown:
                    logger.info(
                        f"{self.channel_info} Setting tournament countdown to {self.tournament_countdown}"
                    )
                    await self.set_tournament_countdown(self.tournament_countdown)
                    await self.send_message_to_all(
                        {"event": "countdown", "countdown": self.tournament_countdown},
                        "tournament",
                    )
            elif (
                time.time() - self.game_state.round_start_time
                <= settings.COUNTDOWN_TIME
            ):
                if self.is_tournament_countdown:
                    self.is_tournament_countdown = False
                self.game_state.countdown = settings.COUNTDOWN_TIME - int(
                    time.time() - self.game_state.round_start_time
                )
            else:
                logger.info(
                    f"{self.channel_info} Countdown finished, setting state to PLAYING"
                )
                self.game_state.countdown = 0
                await self.set_state("PLAYING")
        except Exception as e:
            logger.error(f"{self.channel_info} Error handling countdown: {e}")

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
        # logger.info(
        #     f"Sending message to group_name from game loop: {self.pong_group_name}"
        # )

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
            logger.error(f"{self.channel_info} Error sending message to all: {e}")

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
                # logger.info(
                #     f"player1.up_pressed, new y player 1 paddle: {self.game_state.player1.y}"
                # )
            elif self.game_state.player1.down_pressed:
                new_y = self.game_state.player1.y + settings.PADDLE_SPEED
                if new_y > settings.LOWER_LIMIT:
                    self.game_state.player1.y = settings.LOWER_LIMIT
                else:
                    self.game_state.player1.y = new_y
                # logger.info(
                #     f"player1.down_pressed, new y player 1 paddle: {self.game_state.player1.y}"
                # )

            if self.game_state.player2.up_pressed:
                new_y = self.game_state.player2.y - settings.PADDLE_SPEED
                if new_y < settings.UPPER_LIMIT:
                    self.game_state.player2.y = settings.UPPER_LIMIT
                else:
                    self.game_state.player2.y = new_y
                # logger.info(
                #     f"player2.up_pressed, new y player 2 paddle: {self.game_state.player2.y}"
                # )
            elif self.game_state.player2.down_pressed:
                new_y = self.game_state.player2.y + settings.PADDLE_SPEED
                if new_y > settings.LOWER_LIMIT:
                    self.game_state.player2.y = settings.LOWER_LIMIT
                else:
                    self.game_state.player2.y = new_y
                # logger.info(
                #     f"player2.down_pressed, new y player 2 paddle: {self.game_state.player2.y}"
                # )
        except Exception as e:
            logger.error(f"{self.channel_info} Error moving paddles: {e}")

    def calculate_new_ball_position(self):
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
            logger.error(
                f"{self.channel_info} Error calculating new ball position: {e}"
            )

    def calculate_collisions(self):
        try:
            # top border
            if (
                self.ball_new_y
                <= settings.THICK_BORDER_THICKNESS + settings.BALL_RADIUS
            ):
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
            # left paddle
            if (
                self.ball_new_x
                < settings.PADDING_THICKNESS
                + settings.PADDLE_WIDTH
                + settings.BALL_RADIUS
                and self.game_state.player1.y
                - settings.PADDLE_HEIGHT / 2
                - settings.BALL_RADIUS
                <= self.ball_new_y
                <= self.game_state.player1.y
                + settings.PADDLE_HEIGHT / 2
                + settings.BALL_RADIUS
            ):
                logger.info(f"{self.channel_info} HIT LEFT PADDLE")
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
                    self.ball_new_x = (
                        self.game_state.ball.x
                        + remaining_movement * self.game_state.ball_vector["x"]
                    )
            # right paddle
            elif (
                self.ball_new_x
                > settings.FIELD_WIDTH
                - settings.PADDING_THICKNESS
                - settings.PADDLE_WIDTH
                - settings.BALL_RADIUS
                and self.game_state.player2.y
                - settings.PADDLE_HEIGHT / 2
                - settings.BALL_RADIUS
                <= self.ball_new_y
                <= self.game_state.player2.y
                + settings.PADDLE_HEIGHT / 2
                + settings.BALL_RADIUS
            ):
                logger.info(f"{self.channel_info} HIT RIGHT PADDLE")
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
                    self.ball_new_x = (
                        self.game_state.ball.x
                        - remaining_movement * self.game_state.ball_vector["x"]
                    )
        except Exception as e:
            logger.error(f"{self.channel_info} Error calculating collisions: {e}")

    def get_winner_if_someone_scored(self):
        try:
            if self.ball_new_x >= settings.FIELD_WIDTH - settings.BALL_RADIUS:
                return self.match.player1
            elif self.ball_new_x <= settings.BALL_RADIUS:
                return self.match.player2
            return None
        except Exception as e:
            logger.error(
                f"{self.channel_info} Error getting winner if someone scored: {e}"
            )

    @database_sync_to_async
    def check_win(self):
        try:
            # logger.info("Checking for winner")
            winner = self.get_winner_if_someone_scored()
            if winner:
                logger.info(f"{self.channel_info} we have a winner")
                logger.info(f"{self.channel_info} Winner: {winner}")
                self.match.winner = winner
                self.match.state = "FINISHED"
                self.game_state.state = "FINISHED"
                self.match.winner = winner
                self.running = False
                self.match.save()
        except Exception as e:
            logger.error(f"{self.channel_info} Error checking for winner: {e}")

    async def game_loop(self):

        logger.info(f"{self.channel_info} Game loop started")
        while self.running:
            try:
                # paddles move always, even on countdown
                await sync_to_async(self.move_paddles)()
                if self.game_state.state == "COUNTDOWN":
                    await self.handle_countdown()
                elif self.game_state.state == "PLAYING":
                    # logger.info("Game loop state PLAYING")
                    await sync_to_async(self.calculate_new_ball_position)()
                    await sync_to_async(self.calculate_collisions)()
                    self.game_state.ball.x = self.ball_new_x
                    self.game_state.ball.y = self.ball_new_y
                    await self.check_win()
                if not self.is_tournament_countdown:
                    await self.send_game_state_to_all()
                if self.game_state.state == "FINISHED":
                    logger.info("Game finished")
                    # should we send tournament message instead? or nothing?
                    await self.send_game_state_to_all()
                await asyncio.sleep(1 / settings.FPS)
            except Exception as e:
                logger.error(f"Error in game loop: {e}")
        logger.info(f"{self.channel_info} Game loop finished")
        if self.game_state.state == "FINISHED":
            game_over_message = {
                "event": "game_finished",
                "winner": self.match.winner.alias,
            }
            await self.send_message_to_all(game_over_message, "tournament")

    def stop(self):
        logger.info(f"{self.channel_info} Game loop stopped")
        self.running = False
        if self.loop_task:
            self.loop_task.cancel()
            self.loop_task = None
