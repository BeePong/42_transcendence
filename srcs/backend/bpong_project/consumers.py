import json
from channels.generic.websocket import WebsocketConsumer

class PongConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        data = json.loads(text_data)
        paddle_x = data['paddle_x']
        paddle_y = data['paddle_y']
        ball_x = data['ball_x']
        ball_y = data['ball_y']
        
        # Update game field
        self.update_game_field(paddle_x, paddle_y, ball_x, ball_y)

        # Send updated game state back to client
        self.send(text_data=json.dumps({
            'paddle_x': paddle_x,
            'paddle_y': paddle_y,
            'ball_x': ball_x,
            'ball_y': ball_y,
        }))

    def update_game_field(self, paddle_x, paddle_y, ball_x, ball_y):
        # Your game logic here
        pass