import json
import math
import random
import threading
import time
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from enum import Enum
from django.conf import settings
from django.http import Http404
from asgiref.sync import sync_to_async

# from django.contrib.auth.models import User

from .models import Tournament, Player
from django.shortcuts import get_object_or_404
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer

# import asyncio
# from .ai import ai_bot


class PongConsumer(AsyncWebsocketConsumer):

    tournament = None
    print("PONG CONSUMER root")

    @database_sync_to_async
    def get_tournament_by_id(self, tournament_id):
        try:
            tournament_object = get_object_or_404(
                Tournament, tournament_id=tournament_id
            )
            return tournament_object
        except Tournament.DoesNotExist:
            return None
        except Http404:
            return None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pong_group_name = "tournament_group"
        print("PONG CONSUMER INITIALISED")

    async def connect(self):
        # init tournament if not initialized yet
        if self.__class__.tournament is None:
            tournament_id = self.scope["url_route"]["kwargs"]["tournament_id"]
            # init tournament to new instance of Tournament class
            self.__class__.tournament = await self.get_tournament_by_id(tournament_id)
            if self.__class__.tournament is None:
                print("Tournament not found")
                await self.close(code=4004)
                return

        # accept connection
        await self.accept()
        # close if tournament is over
        if self.__class__.tournament.state == "FINISHED":
            print(
                "User is not authenticated or the tournament is finished, disconnecting"
            )
            await self.close(code=4005)
        # close if not authenticated
        if not (self.scope["user"].is_authenticated):
            print(
                "User is not authenticated or the tournament is finished, disconnecting"
            )
            await self.close(code=4004)
        # add consumer to group

        await self.channel_layer.group_add(self.pong_group_name, self.channel_name)

        # not sure if this bot handling is needed here
        is_bot = self.scope["query_string"].decode().split("=")[1] == "True"
        if is_bot:
            user = {"id": 0, "username": "ai_bot"}
        else:
            user = self.scope["user"]
        # add player to tournament if eligible

        await self.__class__.tournament.connect_player_if_applicable(user)
        await self.__class__.tournament.start_tournament_if_applicable()

    async def disconnect(self, close_code):
        # set player status to false in tournament
        if self.__class__.tournament is not None:
            await self.__class__.tournament.disconnect_player(self.scope["user"])
        # remove consumer from group
        await self.channel_layer.group_discard(self.pong_group_name, self.channel_name)

    def handle_game_message(self, message):
        print("handle_game_message, message:")
        print(message)
        self.__class__.tournament.handle_key_action(
            self.scope["user"], message["key"], message["keyAction"]
        )

    def handle_tournament_message(self, message):
        print("handle_tournament_message, message:")
        print(message)

    @classmethod
    async def send_game_state_to_all(self, match):
        # print("send_game_state_to_all")
        try:
            match_dict = await match.to_dict()
            # print("match_dict", match_dict)
        except Exception as e:
            print(f"Error serialising game state: {e}")
        channel_layer = get_channel_layer()
        try:
            await channel_layer.group_send(
                "tournament_group",
                {
                    "type": "send_game_state",
                    "game_state": match_dict,
                },
            )
        except Exception as e:
            print(f"Error sending game state: {e}")

    async def send_game_state(self, event):
        game_state = event["game_state"]
        try:
            await self.send(text_data=json.dumps(game_state))
        except Exception as e:
            print(f"Error sending game state: {e}")

    # reveive() has to be async because we're using channel layer
    async def receive(self, text_data):
        print("receive")
        print("tournament state:", self.__class__.tournament.state)
        # Use sync_to_async to call the synchronous ORM method
        user_in_tournament = await sync_to_async(
            self.__class__.tournament.is_user_in_tournament
        )(self.scope["user"])
        print("user_in_tournament:", user_in_tournament)
        if self.__class__.tournament.state == "PLAYING" and user_in_tournament:
            try:
                print("before json.loads")
                text_data_json = json.loads(text_data)
                message = text_data_json["message"]
                message_type = text_data_json["type"]
                print("message_type:", message_type)
                if message_type == "tournament":
                    await sync_to_async(self.handle_tournament_message)(message)
                elif message_type == "game":
                    await sync_to_async(self.handle_game_message)(message)
            except Exception as e:
                print("Error in receive method: %s", e)
