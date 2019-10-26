import logging
from threading import Thread, Timer

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
        logging.debug("ReminderSenderParallelService: Recibido " + message)
        jsonvar = self._reminders.jsonify()
        logging.debug("ReminderSenderParallelService: Enviando " + jsonvar)
        self._publisher.publish(jsonvar)


class ReminderTimersService():
    ANSWER_CHANNEL = "/dsh/damaso/reminders/notifications"

    def __init__(self):
        self._timers = {}
        self._publisher = MQTTPublisher(self.ANSWER_CHANNEL)
        self._reminders = ReminderData()
        self._add_id = self._reminders.register_add_callback(self._start_timer)
        self._remove_id = self._reminders.register_remove_callback(self._stop_timer)

    def _start_timer(self, r_id: str):
        secs = self._reminders.get_seconds_to(r_id)
        tmr = Timer(secs, self.notify)
        self._timers[r_id] = tmr
        self._timers[r_id].start()

    def _stop_timer(self, r_id):
        try:
            self._timers.pop(r_id).stop()
        except Exception:
            pass

    def notify(self, r_id: str):
        rmndr = self._reminders.get_reminder(r_id)
        if rmndr is not None:
            self._publisher.publish(rmndr[2])
