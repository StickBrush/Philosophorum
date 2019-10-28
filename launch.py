import argparse
import logging

from orchestrator.proactivity import *
from orchestrator.remind import *
from orchestrator.tv import *

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Orchestrator for the Dámaso project")

    parser.add_argument("--DEBUG", action='store_const', const=logging.DEBUG, default=logging.INFO,
                        metavar='Enables debug-level logging')

    arguments = parser.parse_args()

    logging.basicConfig(level=arguments.DEBUG)

    orch_proac_awaken_service = ProactiveAwakenService()
    orch_proac_awaken_service.start()

    orch_rem_server_service = ReminderSenderParallelService()
    orch_rem_server_service.start()

    orch_rem_timers_service = ReminderTimersService()

    orch_tv_pause_service = TVPauseParallelService()
    orch_tv_pause_service.start()

    orch_tv_channel_service = TVChannelParellelService()
    orch_tv_channel_service.start()

    orch_tv_broadcast_service = TVBroadcastRemindersParallelService()
    orch_tv_broadcast_service.start()
