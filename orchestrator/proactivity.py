from json import dumps
from logging import debug as log
from threading import Thread, Timer

from lib.communicator import MQTTDaemon, MQTTPublisher
from lib.kodiCtrl import KodiRpc
from orchestrator.tv import TVPauseParallelService, TVStopParallelService


class ProactiveAwakenParallelService(Thread):
    LISTEN_CHANNEL = "/dsh/damaso/proactive/awaken"
    ANSWER_CHANNEL = "hermes/hotword/hey_snips/detected"

    def __init__(self):
        Thread.__init__(self)
        self._publisher = MQTTPublisher(self.ANSWER_CHANNEL)
        log("ProactiveAwakenParallelService: Created")

    def run(self):
        log("ProactiveAwakenParallelService: Running")
        MQTTDaemon(self.interact, self.LISTEN_CHANNEL)

    def interact(self, message):
        log("ProactiveAwakenParallelService: Got message " + message)
        self._publisher.publish(dumps({'siteId': 'default', 'modelId': 'hey_snips'}))


class ProactiveManagementParallelService(Thread):
    LISTEN_CHANNEL = "/dsh/damaso/proactive/sensor"
    WAKEUP_CHANNEL = ProactiveAwakenParallelService.LISTEN_CHANNEL
    PAUSE_CHANNEL = TVPauseParallelService.LISTEN_CHANNEL
    STOP_CHANNEL = TVStopParallelService.LISTEN_CHANNEL
    TIMER_DEADLINE = 5.0 * 60.0

    def __init__(self):
        Thread.__init__(self)
        self._kodi = KodiRpc()
        self._timer = None
        self._awakener = MQTTPublisher(self.WAKEUP_CHANNEL)
        self._pauser = MQTTPublisher(self.PAUSE_CHANNEL)
        self._stopper = MQTTPublisher(self.STOP_CHANNEL)
        log("ProactiveManagementParallelService: Created")

    def run(self):
        log("ProactiveManagementParallelService: Running")
        MQTTDaemon(self.interact, self.LISTEN_CHANNEL)

    def interact(self, message):
        log("ProactiveManagementParallelService: Got message " + message)
        if message == "ON":
            if self._kodi.is_playing():
                if self._kodi.is_paused():
                    log("ProactiveManagementParallelService: Playing back")
                    self._pauser.publish("PLAY")
                    if self._timer is not None:
                        log("ProactiveManagementParallelService: Cancelling timer")
                        self._timer.cancel()
                        self._timer = None
                else:
                    log("ProactiveManagementParallelService: No effects")
            else:
                log("ProactiveManagementParallelService: Waking up")
                self._awakener.publish("AWAKEN MY MASTERS")
        else:
            if self._kodi.is_paused():
                log("ProactiveManagementParallelService: No effects")
            else:
                log("ProactiveManagementParallelService: Pausing and starting timer")
                self._pauser.publish("PAUSE")
                self._timer = Timer(self.TIMER_DEADLINE, self.stop)

    def stop(self):
        self._stopper.publish("STOP HAMMERTIME")
