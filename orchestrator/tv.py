from logging import debug as log, warning as logw
from threading import Thread

from lib.communicator import MQTTDaemon
from lib.kodiCtrl import KodiRpc
from lib.reminders import ReminderData


class TVPauseParallelService(Thread):
    LISTEN_CHANNEL = "/dsh/damaso/playing"

    def __init__(self):
        Thread.__init__(self)
        self._kodi = KodiRpc()
        log("TVPauseParallelService: Created")

    def run(self):
        log("TVPauseParallelService: Running")
        MQTTDaemon(self.interact, self.LISTEN_CHANNEL)

    def interact(self, message):
        log("TVPauseParallelService: Got message " + message)
        self._kodi.play_pause()


class TVStopParallelService(Thread):
    LISTEN_CHANNEL = "/dsh/damaso/stop"

    def __init__(self):
        Thread.__init__(self)
        self._kodi = KodiRpc()
        log("TVStopParallelService: Created")

    def run(self):
        log("TVStopParallelService: Running")
        MQTTDaemon(self.interact, self.LISTEN_CHANNEL)

    def interact(self, message):
        log("TVStopParallelService: Got message " + message)
        self._kodi.stop()


class TVChannelParellelService(Thread):
    LISTEN_CHANNEL = "/dsh/damaso/channel"

    def __init__(self):
        Thread.__init__(self)
        self._kodi = KodiRpc()
        log("TVChannelParallelService: Created")

    def run(self):
        log("TVChannelParallelService: Running")
        MQTTDaemon(self.interact, self.LISTEN_CHANNEL)

    def interact(self, message):
        log("TVChannelParallelService: Got message " + message)
        self._kodi.play_channel(message)


class TVBroadcastRemindersParallelService(Thread):
    LISTEN_CHANNEL = "/dsh/damaso/reminders/broadcast"
    TV_CONCEPT = 9

    def __init__(self):
        Thread.__init__(self)
        self._kodi = KodiRpc()
        self._reminders = ReminderData()
        log("TVBroadcastRemindersParallelService: Created")

    def run(self) -> None:
        log("TVBroadcastRemindersParallelService: Running")
        MQTTDaemon(self.interact, self.LISTEN_CHANNEL)

    def interact(self, message):
        log("TVBroadcastRemindersParallelService: Got message " + message)
        broadcast = self._kodi.get_next_time(message)
        if broadcast is not None:
            self._reminders.add_reminder(broadcast.hour, broadcast.minute, broadcast.isoweekday(), self.TV_CONCEPT)
        else:
            logw("TVBroadcastRemindersParallelService: " + message + " not found")
