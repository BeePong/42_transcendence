import asyncio
import json
from django.core.cache import cache
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from django.http import Http404
from django.shortcuts import get_object_or_404

from .game_loop import GameLoop
from .game_state import GameState


import logging

from .models import Match, Player, Tournament

import subprocess

logger = logging.getLogger(__name__)

games = {}


class PongConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tournament = None
        self.tournament_id = None
        self.pong_group_name = None
        self.game_loop = None
        self.is_bot = False
        self.username = None  # for debug
        self.consumer_info = None  # for debug

    # HELPER METHODS

    @sync_to_async
    def form_consumer_info(self):
        return f"[{self.channel_name[-4:]} {self.tournament_id} {self.username}]"

    @database_sync_to_async
    def get_tournament_by_id(self, tournament_id):
        try:
            return get_object_or_404(Tournament, tournament_id=tournament_id)
        except (Tournament.DoesNotExist, Http404):
            logger.error(
                f"{self.consumer_info} Tournament with id {tournament_id} does not exist"
            )
            return None

    @database_sync_to_async
    def get_player_by_user(self, user):
        try:
            player = get_object_or_404(Player, user=user)
            return player
        except Player.DoesNotExist:
            return None
        except Http404:
            return None

    @database_sync_to_async
    def is_tournament_full(self):
        try:
            return self.tournament.players.count() == self.tournament.num_players
        except Exception as e:
            logger.error(
                f"{self.consumer_info} Error checking if tournament is full: {e}"
            )
            return False

    # GAME LOGIC HANDLERS

    def create_game_loop_if_not_exists(self):
        if not games.get(self.tournament_id):
            games[self.tournament_id] = GameLoop(
                self.tournament.current_match, self.tournament_id, self.tournament
            )
            logger.info(
                f"{self.consumer_info} Game loop for match {self.tournament.current_match.game_id} created, games dictionary: {games}"
            )
        else:
            logger.info(
                f"{self.consumer_info} Game loop for match {self.tournament.current_match.game_id} already exists, games dictionary: {games}"
            )

    @database_sync_to_async
    def create_1st_match(self):
        try:
            logger.info(f"{self.consumer_info} Creating 1st match")
            if not self.tournament.current_match:
                logger.info(f"{self.consumer_info} Setting current_match")
                self.tournament.current_match, created = Match.objects.get_or_create(
                    player1=self.tournament.players.all()[0],
                    player2=self.tournament.players.all()[1],
                    tournament=self.tournament,
                )
                self.tournament.save()
                if created:
                    logger.info(f"{self.consumer_info} 1st match created")
                else:
                    logger.info(f"{self.consumer_info} 1st match already exists")
            self.create_game_loop_if_not_exists()
        except Exception as e:
            logger.error(f"{self.consumer_info} Error creating 1st match: {e}")

    @database_sync_to_async
    def determine_tournament_winner(self):
        try:
            logger.info("Determining tournament winner")
            winner = self.tournament.current_match.winner
            self.tournament.winner = winner
            self.tournament.save()
        except Exception as e:
            logger.error(
                f"{self.consumer_info} Error determining tournament winner: {e}"
            )

    @database_sync_to_async
    def destroy_game(self):
        try:
            logger.info(f"{self.consumer_info} Destroying game (commented out)")
            games[self.tournament_id].running = False
            games[self.tournament_id].stop()
            logger.info(f"{self.consumer_info} Game loop stopped")
            del games[self.tournament_id]
            logger.info(f"{self.consumer_info} Game loop deleted")
            self.tournament.current_match = None
            self.tournament.save()
        except Exception as e:
            logger.error(f"{self.consumer_info} Error destroying game: {e}")

    # TODO handle tournamernt state. needs to be set to FINISHED at some point

    @database_sync_to_async
    def form_tournament_finished_message(self):
        winner_info = (
            self.tournament.winner.alias if self.tournament.winner else "unknown"
        )
        return {"event": "tournament_finished", "winner": winner_info}

    @database_sync_to_async
    def is_loop_running(self):
        return games[self.tournament_id].running

    def end_game_callback(self, future):
        asyncio.ensure_future(self.end_game(future))

    async def end_game(self, future):
        try:
            logger.info(f"{self.consumer_info} CALLBACK: Game loop over")
            await self.send_message_to_all(
                {"event": "game_over", "winner": "Player1_alias"}, "tournament"
            )
            logger.info(f"{self.consumer_info} Game loop over")
            await self.determine_tournament_winner()
            logger.info(f"{self.consumer_info} Determining tournament winner")
            await self.send_message_to_all(
                await self.form_tournament_finished_message(), "tournament"
            )
            await self.destroy_game()
            await self.set_tournament(state="FINISHED", is_started=False)
            logger.info(f"{self.consumer_info} Tournament finished")
        except Exception as e:
            logger.error(f"{self.consumer_info} Error ending game: {e}")

    async def start_tournament(self):
        try:
            if await self.get_tournament_property("is_started"):
                logger.info(f"{self.consumer_info} Tournament is already started")
                return
            self.set_tournament(is_started=True)
            logger.info(f"{self.consumer_info} Starting tournament")

            num_players_expected = await self.get_tournament_property("num_players")
            logger.info(
                f"{self.consumer_info} Number of players expected: {num_players_expected}"
            )
            if num_players_expected == 2:
                await self.create_1st_match()
                # TODO this condition is wrong, check for it to work. We only want loop to run once
                is_loop_running = await self.is_loop_running()
                logger.info(
                    f"{self.consumer_info} Game loop running bool: {is_loop_running}"
                )
                if is_loop_running:
                    logger.info("Game loop is already running")
                    return
                logger.info(
                    f"{self.consumer_info} Game loop is not running, starting it"
                )
                await games[self.tournament_id].loop(self.consumer_info)
                games[self.tournament_id].loop_task.add_done_callback(
                    self.end_game_callback
                )

            else:
                logger.info("Not 2 players in tournament")
        except Exception as e:
            logger.error(f"{self.consumer_info} Error starting tournament: {e}")
            pass

    @database_sync_to_async
    def form_new_player_message(self, user):
        return {
            "event": "new_player",
            "player_alias": user.username,
            "num_players_in_tournament": self.tournament.players.count(),
            "num_players": self.tournament.num_players,
        }

    @database_sync_to_async
    def form_countdown_message(self, countdown):
        return {
            "event": "countdown",
            "countdown": countdown,
            "player1_alias": "Player1_alias",
            "player2_alias": "Player2_alias",
        }

    @database_sync_to_async
    def get_player_in_current_match(self, user):
        try:
            if not self.tournament:
                logger.info(
                    f"{self.consumer_info} get_player_in_current_match no tournament"
                )
                return None
            if not self.tournament.current_match:
                logger.info(
                    f"{self.consumer_info} get_player_in_current_match no current match"
                )
                return None
            if not games.get(self.tournament_id):
                logger.info(
                    f"{self.consumer_info} get_player_in_current_match no game in dictionary, this should never happen"
                )
                return None
            if self.tournament.current_match.player1.user == user:
                return 1
            if self.tournament.current_match.player2.user == user:
                return 2
            logger.info(
                f"{self.consumer_info} get_player_in_current_match end of function"
            )
            return None
        except Exception as e:
            logger.error(
                f"{self.consumer_info} Error in get_player_in_current_match: {e}"
            )

    # CONNECTION HANDLERS

    @database_sync_to_async
    def set_tournament(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self.tournament, key):
                setattr(self.tournament, key, value)
        self.tournament.save()

    @database_sync_to_async
    def get_tournament_property(self, propertyKey):
        if hasattr(self.tournament, propertyKey):
            return getattr(self.tournament, propertyKey)
        return None

    def spawn_ai_bot(self):
        try:
            subprocess.Popen(
                ["python", "/beePong/tournament/ai.py", str(self.tournament_id)]
            )
            logger.info(
                f"[{self.channel_name[-4:]} {self.tournament_id} {self.username}] AI bot process spawned for tournament {self.tournament_id}"
            )
        except Exception as e:
            logger.error(
                f"[{self.channel_name[-4:]} {self.tournament_id} {self.username}] Error spawning AI bot: {e}"
            )

    async def connect(self):
        try:

            # Get tournament info from the URL
            self.tournament_id = self.scope["url_route"]["kwargs"]["tournament_id"]
            self.pong_group_name = f"group_{self.tournament_id}"
            if not self.tournament:
                self.tournament = await self.get_tournament_by_id(self.tournament_id)

            query_string = self.scope.get("query_string", b"").decode()
            query_params = dict(
                param.split("=") for param in query_string.split("&") if param
            )
            self.is_bot = query_params.get("is_bot", "False").lower() == "true"

            # logger.info(f"Is bot: {self.is_bot}")

            logger.info(f"Is bot: {self.is_bot}")
            logger.info(f"Tournament: {self.tournament}")

            # Accept the connection always
            await self.channel_layer.group_add(self.pong_group_name, self.channel_name)
            await self.accept()

            tournament_state = await self.get_tournament_property("state")
            logger.info(f"Current tournament state: {tournament_state}")
            tournament_is_started = await self.get_tournament_property("is_started")
            logger.info(f"Current tournament is_started: {tournament_is_started}")
            if (
                self.is_bot
                and tournament_is_started is False
                and tournament_state == "PLAYING"
            ):
                logger.info("Starting solo tournament")
                await self.start_tournament()
            elif tournament_is_started is False and tournament_state == "PLAYING":
                logger.info("Starting regular tournament")
                await self.start_tournament()
            else:
                logger.info("Tournament is not started")

            # And then reject if user is not authenticated or tournament does not exist
            if not self.tournament or not self.scope["user"].is_authenticated:
                await self.disconnect()
                return
            self.username = self.scope["user"].username
            self.consumer_info = await self.form_consumer_info()
            # Check what's going on with the games dictionary
            logger.info(f"{self.consumer_info} Games dictionary: {games}")

        except Exception as e:
            logger.info(f"{self.consumer_info} Error in connect method: {e}")

    def get_tournament_data(self, tournament):
        return {
            "tournament_id": tournament.tournament_id,
            "title": tournament.title,
            "state": tournament.state,
            "num_players": tournament.num_players,
            "players": [player.username for player in tournament.players.all()],
            "winner": tournament.winner.username if tournament.winner else "",
        }

    async def disconnect(self, close_code):
        if self.pong_group_name:
            await self.channel_layer.group_discard(
                self.pong_group_name, self.channel_name
            )

    # SENDING AND RECEIVING MESSAGES

    async def send_message_to_all(self, message, message_type):
        try:
            logger.info(
                f"{self.consumer_info} Sending message of type {message_type} to all in group {self.pong_group_name}"
            )
            await self.channel_layer.group_send(
                self.pong_group_name,
                {
                    "type": "send_message",
                    "message": message,
                    "message_type": message_type,
                },
            )
        except Exception as e:
            logger.info(f"{self.consumer_info} Error sending message to all: {e}")

    # TODO: remove if not needed
    # @database_sync_to_async
    # def get_player_number(self):
    #     # Logic to determine if this is player 1 or player 2
    #     # This could be based on the order of connection, user ID, etc.
    #     # For example:
    #     if self.tournament.players.count() == 1:
    #         return 1
    #     else:
    #         return 2

    # async def send_tournament_state_to_all(self, tournament_data):
    #     await self.channel_layer.group_send(
    #         self.pong_group_name,
    #         {"type": "send_tournament_state", "tournament_message": tournament_data},
    #     )

    async def send_message(self, event):
        try:
            message = event["message"]
            type = event["message_type"]
            text_data = await sync_to_async(json.dumps)(
                {"type": type, "message": message}
            )
            await self.send(text_data=text_data)
        except Exception as e:
            logger.error(f"{self.consumer_info} Error sending message: {e}")

    # async def send_tournament_state(self, event):
    #     await self.send(
    #         text_data=json.dumps(
    #             {"type": "tournament", "message": event["tournament_message"]}
    #         )
    #     )

    async def receive(self, text_data):

        try:
            user = self.scope["user"]
            # only receive messages from players in the current match, ignore otherwise
            if not user.is_authenticated:
                return
            player_number = await self.get_player_in_current_match(user)
            logger.info(
                f"{self.consumer_info} Player number of user {user}: {player_number}"
            )
            if not player_number:
                return
            # Parse the message and pass it to key press handler
            text_data_json = json.loads(text_data)
            message = text_data_json["message"]
            # await sync_to_async(self.set_game_loop)()
            await games[self.tournament_id].handle_key_press(message, player_number)
        except Exception as e:
            logger.error(f"{self.consumer_info} Error receiving message: {e}")
