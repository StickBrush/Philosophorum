import logging
from threading import Thread

from lib.communicator import MQTTDaemon
from lib.kodiCtrl import KodiRpc
from lib.reminders import ReminderData


class TVPauseParallelService(Thread):
    LISTEN_CHANNEL = "/dsh/damaso/playing"

    def __init__(self):
        Thread.__init__(self)
        self._kodi = KodiRpc()

    def run(self):
        MQTTDaemon(self.interact, self.LISTEN_CHANNEL)

    def interact(self, message):
        logging.debug("TVPauseParallelService: Recibido " + message)
        self._kodi.play_pause()


class TVChannelParellelService(Thread):
    LISTEN_CHANNEL = "/dsh/damaso/channel"

    def __init__(self):
        Thread.__init__(self)
        self._kodi = KodiRpc()

    def run(self):
        MQTTDaemon(self.interact, self.LISTEN_CHANNEL)

    def interact(self, message):
        logging.debug("TVChannelParallelService: Recibido " + message)
        self._kodi.play_channel(message)


class TVBroadcastRemindersParallelService(Thread):
    LISTEN_CHANNEL = "/dsh/damaso/reminders/broadcast"
    TV_CONCEPT = 9

    def __init__(self):
        Thread.__init__(self)
        self._kodi = KodiRpc()
        self._reminders = ReminderData()

    def run(self) -> None:
        MQTTDaemon(self.interact, self.LISTEN_CHANNEL)

    def interact(self, message):
        logging.debug("TVBroadcastRemindersParallelService: Recibido " + message)
        broadcast = self._kodi.get_next_time(message)
        if broadcast is not None:
            self._reminders.add_reminder(broadcast.hour, broadcast.minute, broadcast.isoweekday(), self.TV_CONCEPT)
        else:
            logging.warning("TVBroadcastRemindersParallelService: No encontrado " + message)
