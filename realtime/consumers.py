from channels.generic.websockets import JsonWebsocketConsumer
import socket
from realtime.models import Employee

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
        card_data = str(content['card_data'].replace("'","").replace("b'",""))
        try:
            employee = Employee.objects.get(card_id = card_data)
        except:
            status = 'denied'
        else:
            if employee.status == 'granted':
                status = 'granted'
            else:
                status = 'denied'
        try:
            self.socket_send(status)
        except:
            pass
        content['status'] = status
        self.group_send('realtime',content)

    def socket_send(self,status):
        s = socket.socket()
        s.connect(("192.168.0.2", 1234))
        s.send(status.encode())
        s.close()


    def disconnect(self, message, **kwargs):
        """
        Perform things on connection close
        """
        pass