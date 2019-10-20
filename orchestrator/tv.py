from threading import Thread

from lib.communicator import MQTTDaemon
from lib.kodiCtrl import KodiRpc


class TVPauseParallelService(Thread):
    LISTEN_CHANNEL = "/dsh/damaso/playing"

    def __init__(self):
        Thread.__init__(self)
        self.kodi = KodiRpc()

    def run(self):
        MQTTDaemon(self.interact, self.LISTEN_CHANNEL)

    def interact(self, message):
        self.kodi.play_pause()
