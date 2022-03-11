from asgiref.sync import async_to_sync
from channels.consumer import SyncConsumer
from channels.generic.websocket import JsonWebsocketConsumer

from phase3.models import MyUser


class EventConsumer(JsonWebsocketConsumer):
    user_dict = {}

    def connect(self):
        uid = self.scope['path'].rsplit('/', 1)[-1]
        role = MyUser.objects.get(id=uid).role
        self.user_dict[self.channel_name] = (uid, role)
        async_to_sync(self.channel_layer.group_add)(
            uid,
            self.channel_name
        )
        async_to_sync(self.channel_layer.group_add)(
            role,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        print("Closed websocket with code: ", close_code)
        async_to_sync(self.channel_layer.group_discard)(
            self.user_dict[self.channel_name][0],
            self.channel_name
        )
        async_to_sync(self.channel_layer.group_discard)(
            self.user_dict[self.channel_name][1],
            self.channel_name
        )
        self.close()

    def receive_json(self, content, **kwargs):
        print("Received event: {}".format(content))
        self.send_json(content)

    # ------------------------------------------------------------------------------------------------------------------
    # Handler definitions! handlers will accept their corresponding message types. A message with type event.alarm
    # has to have a function event_alarm
    # ------------------------------------------------------------------------------------------------------------------
    def cargo_notify(self, event):
        self.send_json(
            {
                'type': 'cargo.notify',
                'content': event['content']
            }
        )

    def container_notify(self, event):
        self.send_json(
            {
                'type': 'container.notify',
                'content': event['content']
            }
        )

    def contcargo_notify(self, event):
        self.send_json(
            {
                'type': 'contcargo.notify',
                'content': event['content']
            }
        )

    def tracker_notify(self, event):
        self.send_json(
            {
                'type': 'tracker.notify',
                'content': event['content']
            }
        )

    def trackcargo_notify(self, event):
        self.send_json(
            {
                'type': 'trackcargo.notify',
                'content': event['content']
            }
        )
    def trackcontainer_notify(self, event):
        self.send_json(
            {
                'type': 'trackcontainer.notify',
                'content': event['content']
            }
        )
    def user_notify(self, event):
        self.send_json(
            {
                'type': 'user.notify',
                'content': event['content']
            }
        )

