import json
import time
import threading
import random
import math
from channels.generic.websocket import WebsocketConsumer
from enum import Enum
# import asyncio
# from .ai import ai_bot

FIELD_WIDTH = 800
FIELD_HEIGHT = 500
PADDLE_HEIGHT = 100
PADDLE_WIDTH = 26
PADDLE_SPEED = 10
MAX_SCORE = 30
BALL_RADIUS = 15
FPS = 30
PADDING_THICKNESS = 7
THICK_BORDER_THICKNESS = 5
UPPER_LIMIT = PADDING_THICKNESS + PADDLE_HEIGHT / 2
LOWER_LIMIT = FIELD_HEIGHT - PADDING_THICKNESS - PADDLE_HEIGHT / 2

class GameState(Enum):
    COUNTDOWN = 'countdown'
    PLAYING = 'playing'
    FINISHED = 'finished'


def get_larger_random():
    y = 0
    while abs(y) < 0.2:
        y = random.uniform(-1, 1)
    return y

def normalize_vector(x, y):
    magnitude = math.sqrt(x**2 + y**2)
    return {'x': x / magnitude, 'y': y / magnitude}

game_state = {
    'round_start_time': time.time(),
    'state': GameState.COUNTDOWN.value,
    'countdown': 3,
    'ball': {'x': FIELD_WIDTH/2, 'y': FIELD_HEIGHT/2},
    'ball_speed': 10,
    'hit_count': 0,
    'ball_vector': normalize_vector(get_larger_random(), random.uniform(-1, 1)),
    'player1': {
        'player_id': None,
        'player_name': 'vvagapov',
        'score': 0,
        'y': FIELD_HEIGHT/2,
        'up_pressed': False,
        'down_pressed': False
    },
    'player2': {
        'player_id': None,
        'player_name': 'dummy',
        'score': 0,
        'y': FIELD_HEIGHT/2,
        'up_pressed': False,
        'down_pressed': False
    },
    'winner': None
}

def init_new_round(game_state):
    game_state['round_start_time'] = time.time()
    game_state['state'] = GameState.COUNTDOWN.value
    game_state['countdown'] = 3
    game_state['ball'] = {'x': FIELD_WIDTH/2, 'y': FIELD_HEIGHT/2}
    game_state['ball_vector'] = normalize_vector(get_larger_random(), random.uniform(-1, 1))

class GameLoop:

    FIELD_WIDTH = 800
    FIELD_HEIGHT = 500
    PADDLE_HEIGHT = 100
    PADDLE_WIDTH = 26
    PADDLE_SPEED = 10
    MAX_SCORE = 30
    BALL_RADIUS = 15
    FPS = 30
    PADDING_THICKNESS = 7
    THICK_BORDER_THICKNESS = 5
    UPPER_LIMIT = PADDING_THICKNESS + PADDLE_HEIGHT / 2
    LOWER_LIMIT = FIELD_HEIGHT - PADDING_THICKNESS - PADDLE_HEIGHT / 2
    
    _instance = None

    @classmethod
    def get_instance(cls, game_state):
        if cls._instance is None:
            cls._instance = cls(game_state)
            cls._instance.start()
        return cls._instance

    def __init__(self, game_state):
        self.game_state = game_state
        self.thread = threading.Thread(target=self.loop)

    def start(self):
        self.thread.start()

    def loop(self):
        self.game_loop()

    def game_loop(self):
        # Your game loop code here, which can use self.game_state
        while True:
            time.sleep(1/self.FPS)
            if self.game_state['state'] == GameState.COUNTDOWN.value:
                if (time.time() - self.game_state['round_start_time'] <= 3):
                    self.game_state['countdown'] = 3 - int(time.time() - self.game_state['round_start_time'])
                else:
                    self.game_state['countdown'] = 0
                    self.game_state['state'] = GameState.PLAYING.value
            elif self.game_state['state'] == GameState.PLAYING.value:
                # Update the position of the paddles based on the key states
                for player_id in ['player1', 'player2']:
                    if self.game_state[player_id]['up_pressed']:
                        new_y = self.game_state[player_id]['y'] - self.PADDLE_SPEED
                        if new_y < self.UPPER_LIMIT:
                            self.game_state[player_id]['y'] = self.UPPER_LIMIT
                        else:
                            self.game_state[player_id]['y'] = new_y
                            
                    elif self.game_state[player_id]['down_pressed']:
                        new_y = self.game_state[player_id]['y'] + self.PADDLE_SPEED
                        if new_y > self.LOWER_LIMIT:
                            self.game_state[player_id]['y'] = self.LOWER_LIMIT
                        else:
                            self.game_state[player_id]['y'] = new_y
                
                # Calculate next position of the ball
                ball_new_x = self.game_state['ball']['x'] + self.game_state['ball_speed'] * self.game_state['ball_vector']['x']
                ball_new_y = self.game_state['ball']['y'] + self.game_state['ball_speed'] * self.game_state['ball_vector']['y']
                
                # Check for collisions with the game boundaries
                if ball_new_y <= self.THICK_BORDER_THICKNESS + self.BALL_RADIUS:
                    # Calculate the remaining movement after the ball hits the wall
                    remaining_movement = self.THICK_BORDER_THICKNESS + self.BALL_RADIUS - self.game_state['ball']['y']
                    # Reverse the y-component of the ball's direction vector
                    self.game_state['ball_vector']['y'] *= -1
                    # Move the ball the remaining distance in the new direction
                    ball_new_y = self.game_state['ball']['y'] + remaining_movement * self.game_state['ball_vector']['y']
                elif ball_new_y >= self.FIELD_HEIGHT - self.THICK_BORDER_THICKNESS - self.BALL_RADIUS:
                    # Calculate the remaining movement after the ball hits the wall
                    remaining_movement = self.game_state['ball']['y'] + self.BALL_RADIUS - (self.FIELD_HEIGHT - self.THICK_BORDER_THICKNESS)
                    # Reverse the y-component of the ball's direction vector
                    self.game_state['ball_vector']['y'] *= -1
                    # Move the ball the remaining distance in the new direction
                    ball_new_y = self.game_state['ball']['y'] - remaining_movement * self.game_state['ball_vector']['y']

                # instead of left paddle place another wall for debugging
                # handle collisions with left wall
                #if ball_new_x <= self.BALL_RADIUS:
                    # Calculate the remaining movement after the ball hits the wall
                    #remaining_movement = self.BALL_RADIUS - self.game_state['ball']['x']
                    # Reverse the x-component of the ball's direction vector
                    #self.game_state['ball_vector']['x'] *= -1
                    # Move the ball the remaining distance in the new direction
                    #ball_new_x = self.game_state['ball']['x'] + remaining_movement * self.game_state['ball_vector']['x']

                # Collisions with the paddles
                if ball_new_x < self.PADDING_THICKNESS + self.PADDLE_WIDTH + self.BALL_RADIUS and self.game_state['player2']['y'] - self.PADDLE_HEIGHT / 2 - self.BALL_RADIUS <= ball_new_y <= self.game_state['player2']['y'] + self.PADDLE_HEIGHT / 2 + self.BALL_RADIUS:
                    self.game_state['hit_count'] += 1
                    # Calculate the remaining movement after the ball hits the wall
                    remaining_movement = self.PADDING_THICKNESS + self.PADDLE_WIDTH - self.game_state['ball']['x']
                    # Reverse the x-component of the ball's direction vector
                    self.game_state['ball_vector']['x'] *= -1
                    # Move the ball the remaining distance in the new direction
                    ball_new_x = self.game_state['ball']['x'] + remaining_movement * self.game_state['ball_vector']['x']
                if ball_new_x > self.FIELD_WIDTH - self.PADDING_THICKNESS - self.PADDLE_WIDTH - self.BALL_RADIUS and self.game_state['player1']['y'] - self.PADDLE_HEIGHT / 2 - self.BALL_RADIUS <= ball_new_y <= self.game_state['player1']['y'] + self.PADDLE_HEIGHT / 2  + self.BALL_RADIUS:
                    self.game_state['hit_count'] += 1
                    # Calculate the remaining movement after the ball hits the wall
                    remaining_movement = self.game_state['ball']['x'] + self.BALL_RADIUS - (self.FIELD_WIDTH - self.PADDING_THICKNESS - self.PADDLE_WIDTH)
                    # Reverse the x-component of the ball's direction vector
                    self.game_state['ball_vector']['x'] *= -1
                    # Move the ball the remaining distance in the new direction
                    ball_new_x = self.game_state['ball']['x'] - remaining_movement * self.game_state['ball_vector']['x']

                # Update the ball's position
                self.game_state['ball']['x'] = ball_new_x
                self.game_state['ball']['y'] = ball_new_y

                # Check for scoring
                if ball_new_x >= self.FIELD_WIDTH - self.BALL_RADIUS:
                    self.game_state['player1']['score'] += 1
                    if (self.game_state['player1']['score'] == self.MAX_SCORE):
                        self.game_state['winner'] = self.game_state['player1']['player_id']
                        self.game_state['state'] = GameState.FINISHED.value
                    else:
                        init_new_round(game_state)
                elif ball_new_x <= self.BALL_RADIUS:
                    self.game_state['player2']['score'] += 1
                    if (self.game_state['player2']['score'] == self.MAX_SCORE):
                        self.game_state['winner'] = self.game_state['player2']['player_id']
                        self.game_state['state'] = GameState.FINISHED.value
                    else:
                        init_new_round(game_state)
            

class PongConsumer(WebsocketConsumer):
    FIELD_WIDTH = 800
    FIELD_HEIGHT = 500
    PADDLE_HEIGHT = 100
    PADDLE_WIDTH = 26
    PADDLE_SPEED = 10
    MAX_SCORE = 30
    BALL_RADIUS = 15
    FPS = 30
    PADDING_THICKNESS = 7
    THICK_BORDER_THICKNESS = 5
    UPPER_LIMIT = PADDING_THICKNESS + PADDLE_HEIGHT / 2
    LOWER_LIMIT = FIELD_HEIGHT - PADDING_THICKNESS - PADDLE_HEIGHT / 2

    
    game_loop = GameLoop.get_instance(game_state)
    game_thread = threading.Thread(target=game_loop.loop)
    game_thread.start()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def get_player_by_user(self, user):
        if user.username == game_state['player1']['player_name']:
            return 'player1'
        elif user.username == game_state['player2']['player_name']:
            return 'player2'
        else:
            return None

    def send_message(self, message):
        self.send(text_data=json.dumps({
            'message': message
        }))
    
    def connect(self):
        self.accept()
        is_bot = self.scope['query_string'].decode().split('=')[1] == 'True'
        if is_bot:
            user = {'id': 0, 'username': 'ai_bot'}
        else:
            user = self.scope['user']
        # TODO: change this to the actual player id, now latest person who joins is the main player, the other one is dummy
        player = self.get_player_by_user(user)
        if not player is None:
            game_state[player]['player_id'] = user.id
            print("PLAYER CONNECTED: ", player, user)
        print("USER CONNECTED: ", user)
        if player is None:
            print("User is not playing this game, they are a viewer")
        if self.scope['user'].is_authenticated:
            print("authenticated user id: ", self.scope['user'].id)
            print("authenticated user name: ", self.scope['user'].username)
        print ("GAME STATE: ", game_state)

    def disconnect(self, close_code):
        pass

    def handle_tournament_message(self, message):
        self.send_message('Received tournament message: ' + str(message))

    def handle_key_event(self, key, keyAction, player_field):
        if key == 'ArrowUp':
            game_state[player_field]['up_pressed'] = keyAction == 'keydown'
        elif key == 'ArrowDown':
            game_state[player_field]['down_pressed'] = keyAction == 'keydown'

    def handle_game_message(self, message):
        player = self.scope['user']
        key = message['key']
        keyAction = message['keyAction']
        # Update the game state based on the key and action
        if player.id == game_state['player1']['player_id']:
            self.handle_key_event(key, keyAction, 'player1')
        elif player.id == game_state['player2']['player_id']:
            self.handle_key_event(key, keyAction, 'player2')

    
    
    def send_game_state(self):
        # Send the updated game state to all players
        self.send(text_data=json.dumps(game_state))
    
    def receive(self, text_data):
        # TODO: only receive data from users who are playing the current game, ignore everyone else - it's done in handle_game_message function now, but this function would be a better place for this
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        message_type = text_data_json['type']

        if message_type == 'tournament':
            self.handle_tournament_message(message)
        elif message_type == 'game':
            self.handle_game_message(message)
