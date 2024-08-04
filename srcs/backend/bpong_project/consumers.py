import json
from channels.generic.websocket import WebsocketConsumer

class PongConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass
    
    def send_message(self, message):
        self.send(text_data=json.dumps({
            'message': message
        }))

    def handle_tournament_message(self, text_data_json):
        self.send_message('Received tournament message: ' + text_data_json['message'])

    def handle_game_message(self, text_data_json):
        self.send_message('Received game message: ' + text_data_json['message'])

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json['type']

        if message_type == 'tournament':
            self.handle_tournament_message(text_data_json)
        elif message_type == 'game':
            self.handle_game_message(text_data_json)
        else:
            self.send(text_data=json.dumps({
                'error': 'Invalid message type'
            }))

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        self.send_message('Received your message: ' + message)