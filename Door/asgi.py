import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Door.settings.development")
from channels.asgi import get_channel_layer

channel_layer = get_channel_layer()