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
    tournament_id = None
    pong_group_name = None
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
        print("PONG CONSUMER INITIALISED")

    async def connect(self):
        # init tournament if not initialized yet
        if self.tournament_id is None:
            self.tournament_id = self.scope["url_route"]["kwargs"]["tournament_id"]
            self.tournament = await self.get_tournament_by_id(self.tournament_id)
            if self.tournament is None:
                print("CONNECT: Tournament not found")
                await self.close(code=4004)
                return
            else:
                print("CONNECT: Tournament was found and added")
            self.tournament.consumer = self
            await sync_to_async(self.tournament.save)()
        if self.pong_group_name is None:
            self.pong_group_name = f"tournament_group_{self.tournament_id}"
            print("pong_group_name set: ", self.pong_group_name)
            # init tournament to new instance of Tournament class

        print("group_add pong_group_name: ", self.pong_group_name)
        await self.channel_layer.group_add(self.pong_group_name, self.channel_name)
        # accept connection
        await self.accept()
        await self.send(
            text_data=json.dumps({"type": "tournament", "message": "connected"})
        )
        # close if tournament is over
        if self.tournament.state == "FINISHED":
            print(
                "The tournament ",
                self.tournament_id,
                " is finished, disconnecting",
            )
            await self.disconnect(code=4005)
            return
        # close if not authenticated
        if not (self.scope["user"].is_authenticated):
            print("User is not authenticated , disconnecting")
            await self.disconnect(code=4004)
            return
        # add consumer to group

        # not sure if this bot handling is needed here
        is_bot = self.scope["query_string"].decode().split("=")[1] == "True"
        if is_bot:
            user = {"id": 0, "username": "ai_bot"}
        else:
            user = self.scope["user"]

        # TODO: first check if a new user actually joined the tournament
        print("user before connect_player_if_applicable: ", user)
        await self.tournament.connect_player_if_applicable(user)
        print(
            "tournament state check before send_tournament_state_to_all: ",
            self.tournament.state,
        )
        #if self.tournament.state == "NEW":
            #await self.send_tournament_state_to_all("tournament_update")
        await self.tournament.start_tournament_if_applicable()

    async def disconnect(self, close_code):
        # set player status to false in tournament
        if self.tournament is not None:
            await self.tournament.disconnect_player(self.scope["user"])
        # remove consumer from group
        print("group_discard pong_group_name: ", self.pong_group_name)
        await self.channel_layer.group_discard(self.pong_group_name, self.channel_name)

    def handle_game_message(self, message):
        print("handle_game_message, message:")
        print(message)
        self.tournament.handle_key_action(
            self.scope["user"], message["key"], message["keyAction"]
        )

    def handle_tournament_message(self, message):
        print("handle_tournament_message, message:")
        print(message)

    async def send_game_state_to_all(self, match):
        print("send_game_state_to_all, pong_group_name: ", self.pong_group_name)
        try:
            match_dict = await match.to_dict()
            # print("match_dict", match_dict)
        except Exception as e:
            print(f"Error serialising game state: {e}")
        try:
            await self.channel_layer.group_send(
                self.pong_group_name,
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
            print("send_game_state")
            await self.send(
                text_data=json.dumps({"type": "game", "message": game_state})
            )
            print("send_game_state done")
        except Exception as e:
            print(f"Error sending game state: {e}")

    async def send_tournament_state_to_all(self, tournament_message):
        print("send_tournament_state_to_all, pong_group_name: ", self.pong_group_name)
        try:
            await self.channel_layer.group_send(
                self.pong_group_name,
                {
                    "type": "send_tournament_state",
                    "tournament_message": tournament_message,
                },
            )
        except Exception as e:
            print(f"Error sending tournament state: {e}")

    async def send_tournament_state(self, event):
        tournament_message = event["tournament_message"]
        try:
            print("send_tournament_state")
            await self.send(
                text_data=json.dumps(
                    {"type": "tournament", "message": tournament_message}
                )
            )
            print("send_tournament_state done")
        except Exception as e:
            print(f"Error sending tournament state: {e}")

    # reveive() has to be async because we're using channel layer
    async def receive(self, text_data):
        print("receive")
        print("receive tournament state:", self.tournament.state)
        # Use sync_to_async to call the synchronous ORM method
        user_in_tournament = await sync_to_async(self.tournament.is_user_in_tournament)(
            self.scope["user"]
        )
        print("receive user_in_tournament:", user_in_tournament)
        if self.tournament.state == "PLAYING" and user_in_tournament:
            try:
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
