from realtime.consumers import MyConsumer

channel_routing = [
    MyConsumer.as_route(path=r"^/"),
]