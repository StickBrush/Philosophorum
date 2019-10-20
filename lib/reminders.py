import json
import pickle
from datetime import datetime
from os.path import exists
from typing import Union, NoReturn
from uuid import uuid4 as gen_uuid


class ReminderData:
    REMINDER_SAVEFILE = 'reminders.sav'

    def __init__(self):
        self._reminders = []
        self._db_reminders = {}

    def _sort(self):
        self._reminders.sort(key=lambda tup: str(tup[1]) + str(tup[0]), reverse=True)

    def add_reminder(self, hour: int, minute: int, weekday: int, concept: int) -> Union[str, NoReturn]:
        if 0 < hour < 25 and -1 < minute < 61 and 0 < weekday < 8:
            str_time = str(hour) + ":" + str(minute) + ":00"
            r_time = datetime.strptime(str_time, '%H:%M:%S').time()
            r_id = str(gen_uuid())
            reminder = (r_time, weekday, concept, r_id)
            self._reminders.append(reminder)
            self._db_reminders[r_id] = reminder
            self._sort()
            return r_id

    def remove_reminder(self, r_id: str) -> bool:
        if r_id in self._db_reminders:
            reminder = self._db_reminders[r_id]
            self._db_reminders.pop(r_id)
            self._reminders.remove(reminder)
            return True
        else:
            return False

    def get_reminder(self, r_id: str) -> Union[tuple, NoReturn]:
        if r_id in self._db_reminders:
            return self._db_reminders[r_id]

    def get_all_reminders(self) -> list:
        return self._reminders

    def save(self):
        with open(ReminderData.REMINDER_SAVEFILE, 'wb') as savefile:
            pickle.dump(self._db_reminders, savefile)

    def load(self):
        if exists(ReminderData.REMINDER_SAVEFILE):
            with open(ReminderData.REMINDER_SAVEFILE, 'rb') as savefile:
                saved = pickle.load(savefile)
                self._db_reminders = saved
                self._reminders = list(self._db_reminders.values())
                self._sort()

    @staticmethod
    def _get_ms_time(time, weekday: int) -> int:
        now = datetime.now()
        now_weekday = now.isoweekday()
        now_time = now.time()
        if time.hour >= now_time.hour:
            delta_sec = (time.hour - now_time.hour) * 3600
        else:
            delta_sec = (now_time.hour - time.hour) * -3600
        if time.minute >= now_time.minute:
            delta_sec += (time.minute - now_time.minute) * 60
        else:
            delta_sec -= (now_time.minute - time.minute) * 60
        if weekday == now_weekday:
            if time <= now_time:
                delta_sec += 24 * 7 * 3600
        else:
            if weekday < now_weekday:
                delta_sec += 24 * (weekday - now_weekday + 7) * 3600
            else:
                delta_sec += 24 * (weekday - now_weekday) * 3600
        delta_ms = delta_sec * 1000
        return delta_ms

    def jsonify(self) -> str:
        rec_list = []
        for reminder in self._reminders:
            ms = self._get_ms_time(reminder[0], reminder[1])
            concept = reminder[2]
            r_dict = {'tiempo': ms, 'sonido': concept}
            rec_list.append(r_dict)
        json_dict = {'recordatorios': rec_list}
        return json.dumps(json_dict)
