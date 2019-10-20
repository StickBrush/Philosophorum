from threading import Thread

from lib.communicator import MQTTDaemon, MQTTPublisher
from lib.reminders import ReminderData


class ReminderSenderParallelService(Thread):
    LISTEN_CHANNEL = "/dsh/damaso/reminders/requests"
    ANSWER_CHANNEL = "/dsh/damaso/reminders/responses"

    def __init__(self):
        Thread.__init__(self)
        self._reminders = ReminderData()
        self._reminders.load()
        self._publisher = MQTTPublisher(self.ANSWER_CHANNEL)

    def run(self):
        MQTTDaemon(self.interact, self.LISTEN_CHANNEL)

    def interact(self, message):
        self._publisher.publish(self._reminders.jsonify())
