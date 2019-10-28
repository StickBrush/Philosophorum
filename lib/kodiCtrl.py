from datetime import datetime
from json import dumps as dictstr
from logging import debug as log, warning as logw

import requests


# JSON RPC API reference: https://kodi.wiki/view/JSON-RPC_API/v9


class KodiRpc:
    URL: str = "http://localhost:8080/jsonrpc"
    CACHE_VALID_TIME: int = 1200

    def __init__(self):
        self._channelList = {}
        self._playing = False
        self._broadcastsList = []
        log("KodiRpc: Created")

    @classmethod
    def _liststr(cls, lst: list) -> str:
        retstr = '['
        for item in lst:
            retstr = retstr + '"' + item + '", '
        retstr = retstr[:-2]
        retstr = retstr + ']'
        return retstr

    @classmethod
    def _build_json(cls, method: str, request_id: str, params: dict = None) -> str:
        base = '{"jsonrpc": "2.0", '
        json = base + '"method": "' + method + '", "id": "' + request_id + '"'
        if params is not None and len(params) > 0:
            json = json + ', "params": {'
            for param, value in params.items():
                if isinstance(value, str):
                    json = json + '"' + param + '": "' + value + '", '
                elif isinstance(value, dict):
                    json = json + '"' + param + '": ' + dictstr(value) + ", "
                elif isinstance(value, list):
                    json = json + '"' + param + '": ' + cls._liststr(value) + ", "
                else:
                    json = json + '"' + param + '": ' + str(value) + ', '
            json = json[:-2]
            json = json + "}"
        json = json + "}"
        return json

    @classmethod
    def _get_tv_ch_groups(cls, request_id: str) -> list:
        log("KodiRpc: Getting all TV channel groups")
        method = "PVR.GetChannelGroups"
        params = {"channeltype": "tv"}
        rpc_call = cls._build_json(method, request_id, params)
        response = requests.post(url=cls.URL, data=rpc_call)
        return response.json()['result']['channelgroups']

    @classmethod
    def _get_main_ch_group(cls, request_id: str) -> int:
        log("KodiRpc: Getting main channel group")
        ch_groups = cls._get_tv_ch_groups(request_id)
        return ch_groups[0]['channelgroupid']

    @classmethod
    def _get_channels(cls, request_id: str) -> list:
        log("KodiRpc: Getting channels")
        main_ch_group = cls._get_main_ch_group("chg")
        method = "PVR.GetChannels"
        params = {"channelgroupid": main_ch_group}
        rpc_call = cls._build_json(method, request_id, params)
        response = requests.post(url=cls.URL, data=rpc_call)
        return response.json()['result']['channels']

    @classmethod
    def _play_channel(cls, request_id: str, channel_id: int) -> bool:
        log("KodiRpc: Playing channel " + str(channel_id))
        rpc_call = cls._build_json("Player.Open", request_id, {'item': {'channelid': channel_id}})
        response = requests.post(url=cls.URL, data=rpc_call)
        return response.json().get('result') == 'OK'

    def _get_channel_list(self) -> dict:
        log("KodiRpc: Getting channel list")
        if len(self._channelList) > 0:
            return self._channelList
        else:
            log("KodiRpc: Caching channel list")
            chs = self._get_channels("chs")
            for ch in chs:
                if ch['label'][-3:] == ' HD':
                    ch['label'] = ch['label'][:-3]
                    if ch['label'].upper() not in self._channelList:
                        self._channelList[ch['label'].upper()] = ch['channelid']
            return self._channelList

    def _get_channel_id_by_name(self, name: str) -> int:
        log("KodiRpc: Getting channel " + name)
        if len(self._channelList) == 0:
            self._get_channel_list()
        return self._channelList.get(name)

    def _get_channel_broadcasts(self, name: str) -> list:
        log("KodiRpc: Getting broadcasts of " + name)
        channel_id = self._get_channel_id_by_name(name)
        if channel_id is not None:
            rpc_call = self._build_json("PVR.GetBroadcasts", "gbrd", {'channelid': channel_id,
                                                                      'properties': ['starttime']})
            response = requests.post(url=self.URL, data=rpc_call).json()
            if response is None:
                logw("KodiRpc: Kodi has no broadcasts for this channel")
                return []
            else:
                return response['result'].get('broadcasts')
        else:
            logw("KodiRpc: Channel does not exist")
            return []

    def _get_next_broadcasts(self, name: str) -> list:
        log("KodiRpc: Getting next broadcasts of " + name)
        broadcasts = self._get_channel_broadcasts(name)
        if broadcasts is not None:
            return list(filter(
                lambda x: datetime.strptime(x['starttime'], '%Y-%m-%d %H:%M:%S') >= datetime.now(),
                broadcasts))
        else:
            return []

    def _get_all_next_broadcasts(self) -> list:
        log("KodiRpc: Getting all next broadcasts")
        if len(self._channelList) == 0:
            self._get_channel_list()
        if len(self._broadcastsList) == 0:
            log("KodiRpc: Caching broadcasts...")
            for ch in self._channelList:
                self._broadcastsList.extend(self._get_next_broadcasts(ch))
        else:
            self._broadcastsList = list(filter(
                lambda x: datetime.strptime(x['starttime'], '%Y-%m-%d %H:%M:%S') >= datetime.now(),
                self._broadcastsList))
        return self._broadcastsList

    def play_pause(self) -> bool:
        log("KodiRpc: Play/pause request")
        rpc_call = self._build_json("Input.ExecuteAction", "plps", {'action': 'playpause'})
        response = requests.post(url=self.URL, data=rpc_call).json()
        return response.get('result') == 'OK'

    def get_channel_names(self) -> list:
        log("KodiRpc: Getting channel names")
        if len(self._channelList) == 0:
            self._get_channels("chs")
        return list(self._channelList.keys())

    def play_channel(self, channel_name: str) -> bool:
        log("KodiRpc: Request to play " + channel_name)
        channel_id = self._get_channel_id_by_name(channel_name.upper())
        if channel_id is None:
            logw("KodiRpc: Channel not found")
            return False
        else:
            self._playing = True
            return self._play_channel("playch", channel_id)

    def stop(self) -> bool:
        log("KodiRpc: Request to stop")
        if not self._playing:
            logw("KodiRpc: Not playing anything")
            return False
        else:
            rpc_call = self._build_json("Input.ExecuteAction", "stp", {'action': 'stop'})
            response = requests.post(url=self.URL, data=rpc_call).json()
            if response.get('result') == 'OK':
                self._playing = False
                return True
            else:
                return False

    def get_next_time(self, name: str) -> datetime:
        log("KodiRpc: Getting next time schedule for " + name)
        self._get_all_next_broadcasts()
        for br in self._broadcastsList:
            if br['label'].upper() == name.upper():
                return datetime.strptime(br['starttime'], '%Y-%m-%d %H:%M:%S')
