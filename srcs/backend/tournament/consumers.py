import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.http import Http404
from asgiref.sync import sync_to_async
from django.shortcuts import get_object_or_404
from channels.db import database_sync_to_async
from .models import Tournament


class PongConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tournament = None
        self.tournament_id = None
        self.pong_group_name = None

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
                tournament_data = await self.get_tournament_data(self.tournament)
                # Send the tournament data to all clients in the group
                await self.send_tournament_state_to_all(tournament_data)
        except Exception as e:
            print(f"Error in connect method: {e}")

    async def disconnect(self, close_code):
        if self.pong_group_name:
            await self.channel_layer.group_discard(
                self.pong_group_name, self.channel_name
            )

    async def send_tournament_state_to_all(self, tournament_data):
        if self.pong_group_name:
            try:
                await self.channel_layer.group_send(
                    self.pong_group_name,
                    {
                        "type": "send_tournament_state",
                        "tournament_message": tournament_data,
                    },
                )
            except Exception as e:
                print(f"Error sending tournament state: {e}")

    async def send_tournament_state(self, event):
        try:
            message = json.dumps(
                {"type": "tournament", "message": event["tournament_message"]}
            )

            await self.send(text_data=message)
        except Exception as e:
            print(f"Error sending tournament state: {e}")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            # Process the received data here
            print(f"Received data: {data}")
        except json.JSONDecodeError:
            print("Received invalid JSON data")
        except Exception as e:
            print(f"Error in receive method: {e}")
