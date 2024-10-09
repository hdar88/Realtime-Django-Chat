from channels.generic.websocket import WebsocketConsumer
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from asgiref.sync import async_to_sync

import json
from .models import *

class ChatroomConsumer(WebsocketConsumer):

   '''connect to the websocket and join the chatroom group
   @param self: the current consumer instance
   ''' 
    def connect(self):
        self.user = self.scope['user']
        self.chatroom_name = self.scope['url_route']['kwargs']['chatroom_name']
        self.chatroom = get_object_or_404(ChatGroup, group_name=self.chatroom_name)
        
        if self.channel_layer is None:
            raise RuntimeError("Channel layer is not available")
            
        async_to_sync(self.channel_layer.group_add)(
            self.chatroom_name, self.channel_name
        )

        # increment and update current online users count
        if self.user not in self.chatroom.users_online.all():
            self.chatroom.users_online.add(self.user)
            self.update_online_count()

        self.accept()
    
    '''disconnect from the websocket and leave the chatroom group
    @param self: the current consumer instance
    @param close_code: the close code received from the client
    '''
    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.chatroom_name, self.channel_name
        )

        # decrement and update current online users count
        if self.user in self.chatroom.users_online.all():
            self.chatroom.users_online.remove(self.user)
            self.update_online_count()

    '''receive messages from the websocket and broadcast them to the group
    @param self: the current consumer instance
    @param text_data: the text data received from the client
    '''
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        body = text_data_json['body']

        message = GroupMessage.objects.create(
            body = body,
            author = self.user,
            group = self.chatroom
        )

        event = {
            'type': 'message_handler',
            'message_id': message.id,
        }

        async_to_sync(self.channel_layer.group_send)(
            self.chatroom_name, event
        )

    '''broadcast messages to the group
    @param self: the current consumer instance
    @param event: the event data received from the group
    '''    
    def message_handler(self, event):
        message_id = event['message_id']
        message = GroupMessage.objects.get(id=message_id)
        context = {
        'message' : message,
        'user' : self.user,
        }
        html= render_to_string("rt_chat/partials/chat_message_p.html", context= context)
        self.send(text_data=html)
    
    '''update the current online users count in the group
    @param self: the current consumer instance
    '''
    def update_online_count(self):
        online_count = self.chatroom.users_online.count() -1

        event = {
            'type': 'online_count_handler',
            'online_count': online_count,
        }
        async_to_sync(self.channel_layer.group_send)(self.chatroom_name, event)

    '''broadcast the current online users count to the group
    @param self: the current consumer instance
    @param event: the event data received from the group
    '''    
    def online_count_handler(self, event):
        online_count = event['online_count']
        context = {
            'online_count': online_count,
        }
        html= render_to_string("rt_chat/partials/online_count.html", context= context)
        self.send(text_data=html)