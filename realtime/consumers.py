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
            if employee.status == 'granted' or employee.status == "granted_reload":
                status = 'granted'
                content['first_name'] = employee.first_name
                content['last_name'] = employee.last_name
                content['cedula'] = employee.cedula
                content['rh'] = employee.rh
                content['cargo'] = employee.cargo
                content['photo'] = employee.get_photo()
            else:
                status = 'denied'
        try:
            self.socket_send(status)
        except:
            pass
        content['status'] = status
        content['card_data'] = card_data
        self.group_send('realtime',content)

    def socket_send(self,status):
        s = socket.socket()
        s.connect(("0.0.0.0", 1234))
        s.send(status.encode())
        s.close()


    def disconnect(self, message, **kwargs):
        """
        Perform things on connection close
        """
        pass