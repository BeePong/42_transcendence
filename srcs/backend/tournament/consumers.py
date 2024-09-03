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

from django.contrib.auth.models import User

from .models import Tournament, Player
from django.shortcuts import get_object_or_404
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer

# import asyncio


class PongConsumer(AsyncWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tournament = None
        self.tournament_id = None
        self.pong_group_name = None
        print("PONG CONSUMER INITIALISED")

    # @database_sync_to_async
    # def get_tournament_by_id(self, tournament_id):
    #     try:
    #         tournament_object = get_object_or_404(
    #             Tournament, tournament_id=tournament_id
    #         )
    #         return tournament_object
    #     except Tournament.DoesNotExist:
    #         return None
    #     except Http404:
    #         return None

    async def connect(self):
        try:
            if self.tournament_id is None:
                self.tournament_id = self.scope["url_route"]["kwargs"]["tournament_id"]
            print("tournament_id set: ", self.tournament_id)
            if self.pong_group_name is None:
                self.pong_group_name = f"tournament_group_{self.tournament_id}"
            print("pong_group_name set: ", self.pong_group_name)
            await self.channel_layer.group_add(self.pong_group_name, self.channel_name)
            print("group_add done")
            await self.accept()
            print("accept done")
            try:
                await self.send_tournament_state_to_all("hello from tournament message")
            except Exception as e:
                print(f"Error sending tournament state: {e}")
        except Exception as e:
            print("Error in connect method: %s", e)

    async def disconnect(self, code):
        print("group_discard: ", self.pong_group_name)
        await self.channel_layer.group_discard(self.pong_group_name, self.channel_name)

    async def send_tournament_state_to_all(self, tournament_message):
        print("send_tournament_state_to_all: ", self.pong_group_name)
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
            print("send_tournament_state, tournament_message: ", tournament_message)
            await self.send("hello")
            print("send_tournament_state done")
        except Exception as e:
            print(f"Error sending tournament state: {e}")

    # reveive() has to be async because we're using channel layer
    async def receive(self, text_data):
        print("receive")
        # user = self.scope["user"]
        # print("user: ", user)
        try:
            print("text_data: ", text_data)
        except Exception as e:
            print("Error in receive method: %s", e)
