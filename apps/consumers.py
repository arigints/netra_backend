# your_app/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer

class PacketCaptureConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.namespace = self.scope['url_route']['kwargs']['namespace']
        self.pod_name = self.scope['url_route']['kwargs']['pod_name']
        self.group_name = f"packets_{self.namespace}_{self.pod_name}"

        # Join room group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'packet_message',
                'message': message
            }
        )

    async def packet_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))
