from json import loads as dejson
from logging import debug as log, warning as logw
from threading import Thread, Timer
from time import sleep

from lib.communicator import MQTTDaemon, MQTTPublisher
from lib.reminders import ReminderData

import traceback

class ReminderSenderParallelService(Thread):
#    LISTEN_CHANNEL = "/dsh/damaso/reminders/requests"
    ANSWER_CHANNEL = "/dsh/damaso/reminders/responses"

    def __init__(self):
        Thread.__init__(self)
        self._reminders = ReminderData()
        self._reminders.load()
        self._publisher = MQTTPublisher(self.ANSWER_CHANNEL)
        log("ReminderSenderParallelService: Created")

    def run(self):
        MQTTDaemon(self.interact, "/")

    def interact(self, message):
        log("ReminderSenderParallelService: Got message " + message)
        jsonvar = self._reminders.jsonify()
        if jsonvar is not None:
            log("ReminderSenderParallelService: Sending " + jsonvar)
            self._publisher.publish(jsonvar)

class ReminderIDSenderParallelService(Thread):
    LISTEN_CHANNEL = "/dsh/damaso/reminders/requests"
    ANSWER_CHANNEL = "/dsh/damaso/reminders/IDresponses"

    def __init__(self):
        Thread.__init__(self)
        self._reminders = ReminderData()
        self._reminders.load()
        self._publisher = MQTTPublisher(self.ANSWER_CHANNEL)
        log("ReminderIDSenderParallelService: Created")

    def run(self):
        MQTTDaemon(self.interact, self.LISTEN_CHANNEL)

    def interact(self, message):
        try:
            log("ReminderIDSenderParallelService: Got message " + message)
            jsonvar = self._reminders.jsonify_id()
            log("ReminderIDSenderParallelService: Sending " + jsonvar)
            self._publisher.publish(jsonvar)
        except:
            traceback.print_exc()
            pass

    
class ReminderTimersService:
    ANSWER_CHANNEL = "/dsh/damaso/reminders/notifications"

    def __init__(self):
        self._timers = {}
        self._publisher = MQTTPublisher(self.ANSWER_CHANNEL)
        self._reminders = ReminderData()
        self._add_id = self._reminders.register_add_callback(self._start_timer)
        self._remove_id = self._reminders.register_remove_callback(self._stop_timer)
        log("ReminderTimersService: Created and started")

    def _start_timer(self, r_id: str):
        log("ReminderTimersService: Starting timer for " + r_id)
        secs = self._reminders.get_seconds_to(r_id)
        tmr = Timer(secs, self.notify)
        self._timers[r_id] = tmr
        self._timers[r_id].start()

    def _stop_timer(self, r_id):
        log("ReminderTimersService: Stopping timer for " + r_id)
        try:
            self._timers.pop(r_id).stop()
        except Exception:
            logw("ReminderTimersService: Error stopping timer. Probably " + r_id + " does not exist")

    def notify(self, r_id: str):
        log("ReminderTimersService: Notifying reminder " + r_id)
        rmndr = self._reminders.get_reminder(r_id)
        if rmndr is not None:
            self._publisher.publish(rmndr[2])
        sleep(1.0)  # Wait for a second to make sure enough time has passed
        self._reminders.repeat_reminder(r_id)


class ReminderManagementParallelService(Thread):
    LISTEN_CHANNEL = "/dsh/damaso/reminders/management"
    ANSWER_CHANNEL = "/dsh/damaso/reminders/management/ids"

    def __init__(self):
        Thread.__init__(self)
        self._reminders = ReminderData()
        self._publisher = MQTTPublisher(self.ANSWER_CHANNEL)
        log("ReminderManagementParallelService: Created")

    def run(self) -> None:
        MQTTDaemon(self.interact, self.LISTEN_CHANNEL)

    def interact(self, message):
        log("ReminderManagementParallelService: Got message")
        try:
            json = dejson(message)
            log("ReminderManagementParallelService: Unmarshalled message")
            action = json['action']
            if action == 'ADD':
                log("ReminderManagementParallelService: Adding reminder...")
                hour = int(json['hour'])
                minute = int(json['minute'])
                weekday = int(json['weekday'])
                concept = int(json['concept'])
                log("ReminderManagementParallelService: Added " + str(concept) + " reminder @"
                    + str(hour) + ":" + str(minute) + " on days " + str(weekday))
                r_id = self._reminders.add_reminder(hour, minute, weekday, concept)
                self._publisher.publish(r_id)
                ReminderSenderParallelService().interact("")
            else:
                r_id = json['id']
                log("ReminderManagementParallelService: Removing reminder " + r_id)
                self._reminders.remove_reminder(r_id)

        except Exception:
            logw("ReminderManagementParallelService: Unreadable message: " + message)
