import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.http import Http404
from asgiref.sync import sync_to_async
from django.shortcuts import get_object_or_404
from channels.db import database_sync_to_async
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

    @database_sync_to_async
    def get_tournament_by_id(self, tournament_id):
        try:
            return get_object_or_404(Tournament, tournament_id=tournament_id)
        except (Tournament.DoesNotExist, Http404):
            return None

    @database_sync_to_async
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
            }
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
                tournament_data['player_number'] = self.player_number
                await self.send(text_data=json.dumps({
                    'type': 'tournament',
                    'message': tournament_data
                }))

        except Exception as e:
            print(f"Error in connect method: {e}")

    @database_sync_to_async
    def get_player_number(self):
        # Logic to determine if this is player 1 or player 2
        # This could be based on the order of connection, user ID, etc.
        # For example:
        if self.tournament.players.count() == 1:
            return 1
        else:
            return 2

    async def disconnect(self, close_code):
        if self.pong_group_name:
            await self.channel_layer.group_discard(
                self.pong_group_name, self.channel_name
            )

    async def send_tournament_state_to_all(self, tournament_data):
        await self.channel_layer.group_send(
            self.pong_group_name,
            {
                'type': 'send_tournament_state',
                'tournament_message': tournament_data
            }
        )

    async def send_tournament_state(self, event):
        await self.send(text_data=json.dumps({
            'type': 'tournament',
            'message': event['tournament_message']
        }))

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            if data['type'] == 'game':
                await self.update_game_state(data['message'])
        except json.JSONDecodeError:
            print("Received invalid JSON data")
        except Exception as e:
            print(f"Error in receive method: {e}")

    async def update_game_state(self, message):
        if self.tournament:
            player_number = message.get('playerNumber')
            if player_number == 1:
                paddle_y = self.player1_paddle_y
            elif player_number == 2:
                paddle_y = self.player2_paddle_y
            else:
                return  # Invalid player number

            if message['key'] == 'ArrowUp':
                if message['keyAction'] == 'keydown':
                    paddle_y = max(PADDLE_HEIGHT / 2, paddle_y - PADDLE_SPEED)
            elif message['key'] == 'ArrowDown':
                if message['keyAction'] == 'keydown':
                    paddle_y = min(CANVAS_HEIGHT - PADDLE_HEIGHT / 2, paddle_y + PADDLE_SPEED)

            if player_number == 1:
                self.player1_paddle_y = paddle_y
            elif player_number == 2:
                self.player2_paddle_y = paddle_y

            # After updating, send the new state to all clients
            tournament_data = await self.get_tournament_data(self.tournament)
            await self.send_tournament_state_to_all(tournament_data)