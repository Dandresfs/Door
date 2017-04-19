from channels.generic.websockets import JsonWebsocketConsumer

class MyConsumer(JsonWebsocketConsumer):

    http_user = True
    # Set to True if you want it, else leave it out
    strict_ordering = False

    def connection_groups(self, **kwargs):
        """
        Called to return the list of groups to automatically add/remove
        this connection to/from.
        """
        return ["realtime"]

    def connect(self, message, **kwargs):
        """
        Perform things on connection start
        """
        self.message.reply_channel.send({"accept": True})

    def receive(self, content, **kwargs):
        """
        Called when a message is received with decoded JSON content
        """
        # Simple echo
        self.group_send('realtime',content)

    def disconnect(self, message, **kwargs):
        """
        Perform things on connection close
        """
        pass