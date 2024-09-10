import asyncio
import json
from django.core.cache import cache
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from django.http import Http404
from django.shortcuts import get_object_or_404
import random

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
        try:
            logger.info(f"{self.consumer_info} create_game_loop_if_not_exists")
            if not self.tournament.current_match:
                logger.error(f"{self.consumer_info} CUrrent match is empty")
                # raise Exception("current match is empty")
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
        except Exception as e:
            logger.error(
                f"{self.consumer_info} Error in create_game_loop_if_not_exists(): {e}"
            )

    @database_sync_to_async
    def set_current_match(self):
        try:
            logger.info(f"{self.consumer_info} NEW_ADDITION set_current_match()")
            if not self.tournament.current_match:
                logger.info(f"{self.consumer_info} Setting set_current_match()")
                tournament_matches = Match.objects.filter(
                    tournament=self.tournament, state="PLAYING"
                )
                num_tournament_matches = tournament_matches.count()
                logger.info(
                    f"{self.consumer_info} set_current_match() num_tournament_matches: {num_tournament_matches}"
                )
                if num_tournament_matches == 1:
                    logger.info(
                        f"{self.consumer_info} set_current_match() one active match, setting: {tournament_matches.first()}"
                    )
                    self.tournament.current_match = tournament_matches.first()
                    self.tournament.save()
                elif num_tournament_matches == 0:
                    logger.info(
                        f"{self.consumer_info} set_current_match() no active matches"
                    )
                else:
                    raise Exception(
                        f"{self.consumer_info} set_current_match() too many active matches ({num_tournament_matches}), all: {tournament_matches}"
                    )
        except Exception as e:
            logger.error(f"{self.consumer_info} Error in set_current_match(): {e}")

    def create_current_match_if_not_exists(self, player1, player2):
        try:
            logger.info(f"{self.consumer_info} Creating current match")
            if not player1 or not player2:
                raise Exception(
                    f"{self.consumer_info} ERROR Player1 or Player2 are None: {player1}, {player2}"
                )
            logger.info(f"{self.consumer_info} Creating match")
            if self.tournament.current_match == None:
                logger.info(f"{self.consumer_info} Setting current_match")
                self.tournament.current_match, created = Match.objects.get_or_create(
                    player1=player1,
                    player2=player2,
                    tournament=self.tournament,
                )
                self.tournament.save()
                if created:
                    logger.info(f"{self.consumer_info} match created")
                else:
                    logger.info(f"{self.consumer_info} match already exists")
            else:
                logger.info(f"{self.consumer_info} current_match is already set")
        except Exception as e:
            logger.error(
                f"{self.consumer_info} Error in create_current_match_if_not_exists(): {e}"
            )

    @database_sync_to_async
    def create_match(self, player1, player2):
        try:
            self.create_current_match_if_not_exists(player1, player2)
            self.create_game_loop_if_not_exists()
        except Exception as e:
            logger.error(f"{self.consumer_info} Error creating match: {e}")

    # TODO: remove if not used
    @database_sync_to_async
    def get_current_match_winner(self):
        try:
            logger.info("Determining current match winner")
            return self.tournament.current_match.winner
        except Exception as e:
            logger.error(
                f"{self.consumer_info} Error determining current match winner: {e}"
            )

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
    def get_semifinals_winners(self):
        try:
            matches = Match.objects.filter(tournament=self.tournament)
            winners = [match.winner for match in matches]
            num_winners = len(winners)
            if num_winners != 2:
                logger.error(
                    f"{self.consumer_info} Number of winners is not 2, but {num_winners}"
                )
                return None
            return winners
        except Exception as e:
            logger.error(f"{self.consumer_info} Error getting semifinals winners: {e}")

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
        loop = games.get(self.tournament_id)
        if not loop:
            return False
        return loop.running

    def second_game_callback(self, future):
        asyncio.ensure_future(self.end_second_game(future))

    async def end_second_game(self, future):
        try:
            # finalise second game
            await self.destroy_game()
            # create final game
            player1, player2 = await self.get_players_for_final_match()
            await self.create_match(player1, player2)
            # run final game
            is_loop_running = await self.is_loop_running()
            logger.info(
                f"{self.consumer_info} Final game loop running bool: {is_loop_running}"
            )
            if is_loop_running:
                logger.info("Final game loop is already running")
                return
            logger.info(
                f"{self.consumer_info} Final game loop is not running, starting it"
            )
            await games[self.tournament_id].loop(self.consumer_info)
            # add callback for the end of the final game
            games[self.tournament_id].loop_task.add_done_callback(
                self.final_game_callback
            )
        except Exception as e:
            logger.error(f"{self.consumer_info} Error ending final game: {e}")

    def final_game_callback(self, future):
        asyncio.ensure_future(self.end_final_game(future))

    async def end_final_game(self, future):
        try:
            logger.info(f"{self.consumer_info} CALLBACK: final game over")
            await self.determine_tournament_winner()
            await self.destroy_game()
            await self.finish_tournament()
        except Exception as e:
            logger.error(f"{self.consumer_info} Error ending final game: {e}")

    @database_sync_to_async
    def get_two_random_players(self):
        try:
            matches = Match.objects.filter(tournament=self.tournament)
            num_matches = matches.count()
            player1, player2 = None, None
            players = self.tournament.players.all()
            # TODO: remove the below, debug only
            if not players:
                logger.error(
                    f"{self.consumer_info} get_two_random_players() players is None"
                )
                raise Exception(
                    f"{self.consumer_info} ERROR get_two_random_players(): players is None"
                )
            num_players_in_tournament = players.count()
            logger.info(
                f"{self.consumer_info} get_two_random_players() Number of players in tournament: {num_players_in_tournament}"
            )
            if num_players_in_tournament != 4 and num_players_in_tournament != 2:
                raise Exception(
                    f"{self.consumer_info} ERROR get_two_random_players(): Number of players in tournament is not 2 or 4, but {num_players_in_tournament}"
                )
            if num_matches == 0 or num_players_in_tournament == 2:
                player1 = players[0]
                player2 = players[1]
            elif num_matches == 1:
                if num_players_in_tournament != 4:
                    raise Exception(
                        f"{self.consumer_info} ERROR get_two_random_players(): Number of players should be 4 because match already exists, but it's {num_players_in_tournament}"
                    )
                player1 = players[2]
                player2 = players[3]
            if (player1 is None) or (player2 is None):
                raise Exception(
                    f"{self.consumer_info} ERROR get_two_random_players(): One of the players is None: {player1}, {player2}"
                )
            return player1, player2
        except Exception as e:
            logger.error(f"{self.consumer_info} ERROR getting random players: {e}")

    @database_sync_to_async
    def get_players_for_final_match(self):
        try:
            matches = Match.objects.filter(tournament=self.tournament)
            num_matches = matches.count()
            if num_matches != 2:
                logger.error(
                    f"{self.consumer_info} Number of matches is not 2, but {num_matches}"
                )
                return None
            player1 = matches[0].winner
            player2 = matches[1].winner
            if (player1 is None) or (player2 is None):
                logger.error(
                    f"{self.consumer_info} ERROR get_players_for_final_match(): One of the players is None"
                )
                raise Exception(
                    f"{self.consumer_info} ERROR get_players_for_final_match(): One of the players is None: {player1}, {player2}"
                )
            return player1, player2
        except Exception as e:
            logger.error(
                f"{self.consumer_info} Error getting players for final match: {e}"
            )

    def end_game_callback(self, future):
        asyncio.ensure_future(self.end_game(future))

    async def finish_tournament(self):
        try:
            await self.send_message_to_all(
                await self.form_tournament_finished_message(), "tournament"
            )
            await self.set_tournament(state="FINISHED", is_started=False)
            logger.info(f"{self.consumer_info} Tournament finished")
        except Exception as e:
            logger.error(f"{self.consumer_info} Error finishing tournament: {e}")

    async def end_game(self, future):
        try:

            logger.info(f"{self.consumer_info} CALLBACK: Game loop over")
            num_players_expected = await self.get_tournament_property("num_players")

            if num_players_expected == 2:
                # try to replace this with end_final_game(), if future is not necessary
                await self.determine_tournament_winner()
                await self.destroy_game()
                await self.finish_tournament()

            elif num_players_expected == 4:
                # finalise first game
                await self.destroy_game()
                # create second game
                player1, player2 = await self.get_two_random_players()
                await self.create_match(player1, player2)
                # run second game
                is_loop_running = await self.is_loop_running()
                logger.info(
                    f"{self.consumer_info} Game loop running bool: {is_loop_running}"
                )
                if is_loop_running:
                    logger.info("Game loop is already running")
                    return
                logger.info(
                    f"{self.consumer_info} end_game() Game loop is not running, starting it"
                )
                await games[self.tournament_id].loop(self.consumer_info)
                # add callback for the end of the second game
                games[self.tournament_id].loop_task.add_done_callback(
                    self.second_game_callback
                )

        except Exception as e:
            logger.error(f"{self.consumer_info} Error ending game: {e}")

    async def start_tournament(self):
        try:
            if (
                await self.get_tournament_property("is_started")
                # or await self.get_tournament_property("current_match") is not None
                # or await self.get_tournament_property("state") != "PLAYING"
            ):
                logger.info(
                    f"{self.consumer_info} NEW_ADDITION Tournament is already started"
                )
                return
            else:
                logger.info(
                    f"{self.consumer_info} Tournament is not started yet, proceeding to start"
                )
            await self.set_tournament(is_started=True)
            logger.info(f"{self.consumer_info} Starting tournament")

            # num players for debugging only
            num_players_expected = await self.get_tournament_property("num_players")
            logger.info(
                f"{self.consumer_info} Number of players expected in starting tournament: {num_players_expected}"
            )
            # create first match with 2 random players
            player1, player2 = await self.get_two_random_players()
            await self.create_match(player1, player2)
            # start game loop for first match
            is_loop_running = await self.is_loop_running()
            logger.info(
                f"{self.consumer_info} Game loop running bool: {is_loop_running}"
            )
            if is_loop_running:
                logger.info(f"{self.consumer_info} Game loop is already running")
                return

            logger.info(f"{self.consumer_info} Game loop is not running, starting it")
            if not games.get(self.tournament_id):
                logger.error(f"{self.consumer_info} no loop to start!")
                return
            await games[self.tournament_id].loop(self.consumer_info)
            # add callback for the end of the game
            games[self.tournament_id].loop_task.add_done_callback(
                self.end_game_callback
            )

        except Exception as e:
            logger.error(f"{self.consumer_info} Error starting tournament: {e}")

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

            # Accept the connection always
            await self.channel_layer.group_add(self.pong_group_name, self.channel_name)
            await self.accept()

            # And then reject if user is not authenticated or tournament does not exist
            if not self.tournament or not self.scope["user"].is_authenticated:
                await self.disconnect()
                return
            self.username = self.scope["user"].username
            self.consumer_info = await self.form_consumer_info()

            logger.info(f"{self.consumer_info} Is bot: {self.is_bot}")
            logger.info(f"{self.consumer_info} Tournament: {self.tournament}")

            tournament_state = await self.get_tournament_property("state")
            logger.info(
                f"{self.consumer_info} Current tournament state: {tournament_state}"
            )
            tournament_is_started = await self.get_tournament_property("is_started")
            logger.info(
                f"{self.consumer_info} Current tournament is_started: {tournament_is_started}"
            )

            if (
                self.is_bot
                and tournament_is_started is False
                and tournament_state == "PLAYING"
            ):
                logger.info(
                    f"{self.consumer_info} AI Bot opponent, so we're NOT starting solo tournament"
                )
                # asyncio.sleep(0.1)
                await self.start_tournament()
            elif tournament_is_started is False and tournament_state == "PLAYING":
                logger.info(f"{self.consumer_info} Starting regular tournament")
                await self.start_tournament()
            else:
                logger.info(f"{self.consumer_info} Tournament is not started")

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
            logger.info(f"{self.consumer_info} receive()")
            if not await self.get_tournament_property("current_match"):
                self.set_current_match()
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
