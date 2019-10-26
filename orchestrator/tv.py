import logging
from threading import Thread

from lib.communicator import MQTTDaemon
from lib.kodiCtrl import KodiRpc


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
