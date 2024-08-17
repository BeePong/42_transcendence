import json
import time
import threading
from channels.generic.websocket import WebsocketConsumer

class PongConsumer(WebsocketConsumer):
    FIELD_WIDTH = 800
    FIELD_HEIGHT = 500
    PADDLE_HEIGHT = 100
    PADDLE_WIDTH = 20
    PADDLE_SPEED = 10
    BALL_RADIUS = 15
    FPS = 60
    UPPER_BORDER_THICKNESS = 20
    UPPER_LIMIT = UPPER_BORDER_THICKNESS + PADDLE_HEIGHT / 2
    LOWER_LIMIT = FIELD_HEIGHT - UPPER_BORDER_THICKNESS - PADDLE_HEIGHT / 2

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.game_state = {
            'active': False,
            'ball': {'x': 300, 'y': 300},
            'ball_speed': 5,
            'ball_vector': {'x': 1, 'y': 1},
            'player1': {'y': self.FIELD_HEIGHT/2, 'up_pressed': False, 'down_pressed': False},
            'player2': {'y': self.FIELD_HEIGHT/2, 'up_pressed': False, 'down_pressed': False}
        }
        self.game_thread = threading.Thread(target=self.game_loop)
        self.game_thread.start()
    
    def send_message(self, message):
        self.send(text_data=json.dumps({
            'message': message
        }))
    
    def connect(self):
        self.accept()
        # Send message to client
        self.send_message('You are connected by websockets!')

    def disconnect(self, close_code):
        pass

    def handle_tournament_message(self, text_data_json):
        self.send_message('Received tournament message: ' + str(text_data_json['message']))

    def handle_game_message(self, text_data_json):
        player_id = text_data_json['message']['player_id']
        key = text_data_json['message']['key']
        keyAction = text_data_json['message']['keyAction']
        # Update the game state based on the key and action

        # Send the updated game state to all players
        if key == 'ArrowUp':
            print("ArrowUp")
            self.game_state['player1']['up_pressed'] = keyAction == 'keydown'
        elif key == 'ArrowDown':
            print("ArrowDown")
            self.game_state['player1']['down_pressed'] = keyAction == 'keydown'
    
    def game_loop(self):
        while True:
            time.sleep(1/self.FPS)
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
            #move ball
            self.game_state['ball']['x'] += self.game_state['ball_speed'] * self.game_state['ball_vector']['x']
            self.game_state['ball']['y'] += self.game_state['ball_speed'] * self.game_state['ball_vector']['y']

            # Check for collisions with the game boundaries
            if self.game_state['ball']['y'] <= self.UPPER_LIMIT or self.game_state['ball']['y'] >= self.LOWER_LIMIT - self.BALL_RADIUS:
                # Reverse the y-component of the ball's direction vector
                self.game_state['ball_vector']['y'] *= -1

            # Check for collisions with the paddles
            if self.game_state['ball']['x'] <= self.PADDLE_WIDTH and self.game_state['player2']['y'] <= self.game_state['ball']['y'] <= self.game_state['player2']['y'] + self.PADDLE_HEIGHT:
                # Reverse the x-component of the ball's direction vector
                self.game_state['ball_vector']['x'] *= -1
            elif self.game_state['ball']['x'] >= self.FIELD_WIDTH - self.PADDLE_WIDTH - self.BALL_RADIUS and self.game_state['player1']['y'] <= self.game_state['ball']['y'] <= self.game_state['player1']['y'] + self.PADDLE_HEIGHT:
            # Reverse the x-component of the ball's direction vector
                self.game_state['ball_vector']['x'] *= -1

            # Send the updated game state to all players
            self.send(text_data=json.dumps(self.game_state))

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        # TODO: remove line below, that doesn't seem right
        # self.send_message(text_data=json.dumps({"message": message}))
        message_type = text_data_json['type']

        if message_type == 'tournament':
            self.handle_tournament_message(text_data_json)
        elif message_type == 'game':
            self.handle_game_message(text_data_json)
        else:
            self.send(text_data=json.dumps({
                'error': 'Invalid message type'
            }))
