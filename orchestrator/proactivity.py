from json import dumps
from threading import Thread

from lib.communicator import MQTTDaemon, MQTTPublisher


class ProactiveAwakenService(Thread):
    LISTEN_CHANNEL = "/dsh/damaso/proactive"
    ANSWER_CHANNEL = "hermes/hotword/hey_snips/detected"

    def __init__(self):
        Thread.__init__(self)
        self._publisher = MQTTPublisher(self.ANSWER_CHANNEL)

    def run(self):
        MQTTDaemon(self.interact, self.LISTEN_CHANNEL)

    def interact(self, message):
        self._publisher.publish(dumps({'siteId': 'default', 'modelId': 'hey_snips'}))
