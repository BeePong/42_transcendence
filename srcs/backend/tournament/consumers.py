import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.http import Http404
from asgiref.sync import sync_to_async
from django.shortcuts import get_object_or_404
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from .game_state import GameState

game_states = {}
from .models import Tournament

CANVAS_HEIGHT = 500  # Adjust these values as needed
CANVAS_WIDTH = 800
PADDLE_SPEED = 5
PADDLE_HEIGHT = 100
PADDLE_WIDTH = 10
BALL_SIZE = 10


class PongConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tournament = None
        self.tournament_id = None
        self.pong_group_name = None
        self.player1_paddle_y = CANVAS_HEIGHT / 2
        self.player2_paddle_y = CANVAS_HEIGHT / 2
        self.ball_x = CANVAS_WIDTH / 2
        self.ball_y = CANVAS_HEIGHT / 2
        self.player1_score = 0
        self.player2_score = 0

    # HELPER METHODS

    @database_sync_to_async
    def get_tournament_by_id(self, tournament_id):
        try:
            return get_object_or_404(Tournament, tournament_id=tournament_id)
        except (Tournament.DoesNotExist, Http404):
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
            print("Error in is_tournament_full method: %s", e)
            return False

    # GAME LOGIC HANDLERS

    async def handle_key_press(self, message, user):
        try:
            print("handle_key_press()")
            player = await self.get_player_by_user(user)
            if not player:
                return
            match = await self.get_current_match(player)
            print("handle_key_press() match ", match)
            if not match:
                return

        except Exception as e:
            print("Error in handle_key_press method: %s", e)
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

    # CONNECTION HANDLERS

    # async def connect(self):
    #     try:

    #         # Get tournament info from the URL
    #         self.tournament_id = self.scope["url_route"]["kwargs"]["tournament_id"]
    #         self.pong_group_name = f"group_{self.tournament_id}"
    #         self.tournament = await self.get_tournament_by_id(self.tournament_id)

    #         # Accept the connection always
    #         await self.channel_layer.group_add(self.pong_group_name, self.channel_name)
    #         await self.accept()

    #         # And then reject if user is not authenticated or tournament does not exist
    #         if not self.tournament or not self.scope["user"].is_authenticated:
    #             await self.disconnect()
    #             return

    #         # Send a message to all users that a new player has joined the tournament ? or should it be handled in views.py?
    #         message = await self.form_new_player_message(self.scope["user"])
    #         await self.send_message_to_all(message, "tournament")

    #         # await self.add_player_to_tournament(self.scope["user"])

    #         if await self.is_tournament_full():
    #             print("Tournament is full, starting countdown")
    #             for countdown in range(3, 0, -1):
    #                 countdown_message = await self.form_countdown_message(countdown)
    #                 await self.send_message_to_all(countdown_message, "tournament")
    #                 await asyncio.sleep(1)
    #         else:
    #             print("Tournament is not full, waiting for more players to join")
    # Send updated tournament state to all users
    # try:
    #     await self.send_tournament_state_to_all("hello from tournament message")
    # except Exception as e:
    #     print(f"Error sending tournament state: {e}")
    def get_tournament_data(self, tournament):
        return {
            "tournament_id": tournament.tournament_id,
            "title": tournament.title,
            "state": tournament.state,
            "num_players": tournament.num_players,
            "players": [player.username for player in tournament.players.all()],
            "winner": tournament.winner.username if tournament.winner else "",
            "game_data": {
                "player1_paddle_y": self.player1_paddle_y,
                "player2_paddle_y": self.player2_paddle_y,
                "ball": {
                    "x": self.ball_x,
                    "y": self.ball_y,
                },
                "player1_score": self.player1_score,
                "player2_score": self.player2_score,
            },
        }

    async def connect(self):
        try:
            self.tournament_id = self.scope["url_route"]["kwargs"]["tournament_id"]
            self.pong_group_name = f"tournament_group_{self.tournament_id}"

            await self.channel_layer.group_add(self.pong_group_name, self.channel_name)
            await self.accept()

            # Fetch the tournament data
            self.tournament = await self.get_tournament_by_id(self.tournament_id)
            if self.tournament:
                # Determine which player this client is
                self.player_number = await self.get_player_number()

                # Send initial state including player number
                tournament_data = await self.get_tournament_data(self.tournament)
                tournament_data["player_number"] = self.player_number
                await self.send(
                    text_data=json.dumps(
                        {"type": "tournament", "message": tournament_data}
                    )
                )

        except Exception as e:
            print(f"Error in connect method: {e}")

    async def disconnect(self, close_code):
        if self.pong_group_name:
            await self.channel_layer.group_discard(
                self.pong_group_name, self.channel_name
            )

    # SENDING AND RECEIVING MESSAGES

    async def send_message_to_all(self, message, message_type):
        print("send_message_to_all() in ", self.pong_group_name)

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
            print(f"Error sending message to all: {e}")

    # TODO: remove if not needed
    @database_sync_to_async
    def get_player_number(self):
        # Logic to determine if this is player 1 or player 2
        # This could be based on the order of connection, user ID, etc.
        # For example:
        if self.tournament.players.count() == 1:
            return 1
        else:
            return 2

    async def send_tournament_state_to_all(self, tournament_data):
        await self.channel_layer.group_send(
            self.pong_group_name,
            {"type": "send_tournament_state", "tournament_message": tournament_data},
        )

    async def send_message(self, event):
        message = event["message"]
        type = event["message_type"]
        try:
            text_data = await sync_to_async(json.dumps)(
                {"type": type, "message": message}
            )
            await self.send(text_data=text_data)
        except Exception as e:
            print(f"Error sending tournament state: {e}")

    async def send_tournament_state(self, event):
        await self.send(
            text_data=json.dumps(
                {"type": "tournament", "message": event["tournament_message"]}
            )
        )

    async def receive(self, text_data):
        # my version below
        # try:
        #     print("receive()")
        #     user = self.scope["user"]
        #     print("receive() user ", user)
        #     # only receive messages from players in the current match, ignore otherwise
        #     if not user.is_authenticated:
        #         return
        #     match_ongoing = await self.is_match_ongoing()
        #     if not match_ongoing:
        #         return
        #     is_user_in_current_match = await self.is_user_in_current_match(user)
        #     if not is_user_in_current_match:
        #         return
        #     # Parse the message and pass it to key press handler
        #     text_data_json = json.loads(text_data)
        #     message = text_data_json["message"]
        #     await self.handle_key_press(message, user)
        # except Exception as e:
        #     print("Error in receive method: %s", e)
        #     pass
        try:
            data = json.loads(text_data)
            if data["type"] == "game":
                await self.update_game_state(data["message"])
        except json.JSONDecodeError:
            print("Received invalid JSON data")

        except Exception as e:
            print(f"Error in receive method: {e}")

    async def update_game_state(self, message):
        if self.tournament:
            player_number = message.get("playerNumber")
            if player_number == 1:
                paddle_y = self.player1_paddle_y
            elif player_number == 2:
                paddle_y = self.player2_paddle_y
            else:
                return  # Invalid player number

            if message["key"] == "ArrowUp":
                if message["keyAction"] == "keydown":
                    paddle_y = max(PADDLE_HEIGHT / 2, paddle_y - PADDLE_SPEED)
            elif message["key"] == "ArrowDown":
                if message["keyAction"] == "keydown":
                    paddle_y = min(
                        CANVAS_HEIGHT - PADDLE_HEIGHT / 2, paddle_y + PADDLE_SPEED
                    )

            if player_number == 1:
                self.player1_paddle_y = paddle_y
            elif player_number == 2:
                self.player2_paddle_y = paddle_y

            # After updating, send the new state to all clients
            tournament_data = await self.get_tournament_data(self.tournament)
            await self.send_tournament_state_to_all(tournament_data)
