import json
from channels.generic.websocket import WebsocketConsumer

class PongConsumer(WebsocketConsumer):
    FIELD_WIDTH = 800
    FIELD_HEIGHT = 500
    PADDLE_WIDTH = 10
    PADDLE_HEIGHT = 100
    BALL_RADIUS = 15

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.game_state = {
            'active': False,
            'ball_x': {'x': 0, 'y': 0},
            'ball_speed': 5,
            'ball_vector': {'x': 1, 'y': 1},
            'paddles': {}
        }
    
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
        paddle_y = text_data_json['message']['paddle_y']
        # Update the game state
        self.game_state['paddles'][player_id] = {'y': paddle_y}
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
