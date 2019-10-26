from orchestrator.proactivity import *
from orchestrator.remind import *
from orchestrator.tv import *

if __name__ == '__main__':
    orch_proac_awaken_service = ProactiveAwakenService()
    orch_proac_awaken_service.start()

    orch_rem_server_service = ReminderSenderParallelService()
    orch_rem_server_service.start()

    orch_tv_pause_service = TVPauseParallelService()
    orch_tv_pause_service.start()

    orch_tv_channel_service = TVChannelParellelService()
    orch_tv_channel_service.start()
