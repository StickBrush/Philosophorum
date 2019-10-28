from logging import debug as log

import paho.mqtt.client as mqtt


class MQTTDaemon:

    def __init__(self, action, topic: str):
        self.action = action
        self.client = mqtt.Client()
        self.client.on_message = self.__on_message
        self.client.connect("localhost")
        self.client.subscribe(topic)
        self.client.loop_forever()

    def __on_message(self, client, userdata, message):
        log("MQTTDaemon: Message got")
        self.action(str(message.payload.decode("utf-8")))


class MQTTPublisher:

    def __init__(self, topic: str):
        self.client = mqtt.Client()
        self.client.connect("localhost")
        self.topic = topic

    def publish(self, message: str):
        self.client.publish(self.topic, message)
        log("MQTTPublisher: Message published")
