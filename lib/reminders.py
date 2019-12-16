import json
import pickle
from datetime import datetime
from logging import debug as log, warning as logw
from os.path import exists
from threading import Timer
from typing import Union, NoReturn
from uuid import uuid4 as gen_uuid

from singleton_decorator import singleton


@singleton
class ReminderData:

    def __init__(self):
        self._REMINDER_SAVEFILE = 'reminders.sav'
        self._REMINDER_AUTOSAVE_INTERVAL_SECONDS = 600
        self._NON_REPEATING_REMINDER_CONCEPTS = [7]
        self._reminders = []
        self._db_reminders = {}
        self._add_callbacks = {}
        self._remove_callbacks = {}
        log("ReminderData: Created")
        self.load()
        self._autosave()

    def _autosave(self):
        log("ReminderData: Re-enabling autosave")
        self._timer = Timer(self._REMINDER_AUTOSAVE_INTERVAL_SECONDS, self.save)
        self._timer.start()

    def _sort(self):
        log("ReminderData: Sorting...")
        self._reminders.sort(key=lambda tup: str(tup[1]) + str(tup[0]), reverse=True)

    def register_add_callback(self, f: callable) -> str:
        log("ReminderData: Registering new add callback")
        identifier = str(gen_uuid())
        self._add_callbacks[identifier] = f
        log("ReminderData: Registered " + identifier)
        return identifier

    def deregister_add_callback(self, identifier: str) -> bool:
        log("ReminderData: Deregistering add callback")
        if identifier in self._add_callbacks:
            self._add_callbacks.pop(identifier)
            return True
        else:
            logw("ReminderData: Callback not found")
            return False

    def add_reminder(self, hour: int, minute: int, weekday: int, concept: int) -> Union[str, NoReturn]:
        log("ReminderData: Adding reminder...")
        if 0 < hour < 25 and -1 < minute < 61 and 0 < weekday < 8:
            str_time = str(hour) + ":" + str(minute) + ":00"
            r_time = datetime.strptime(str_time, '%H:%M:%S').time()
            r_id = str(gen_uuid())
            reminder = (r_time, weekday, concept, r_id)
            log("ReminderData: Created reminder " + r_id)
            self._reminders.append(reminder)
            log(self._reminders)
            self._db_reminders[r_id] = reminder
            self._sort()
            log("ReminderData: Executing add callbacks")
            for f in self._add_callbacks.values():
                f(r_id)
            return r_id

    def repeat_reminder(self, r_id: str) -> bool:
        log("ReminderData: Repeating reminder " + r_id)
        if r_id in self._db_reminders:
            if self._db_reminders[r_id][2] in self._NON_REPEATING_REMINDER_CONCEPTS:
                log("ReminderData: Non-repeating reminder, ignoring...")
                return True
            for f in self._add_callbacks.values():
                f(r_id)
            return True
        else:
            logw("ReminderData: Reminder not found")
            return False

    def register_remove_callback(self, f: callable) -> str:
        log("ReminderData: Registering new remove callback")
        identifier = str(gen_uuid())
        self._remove_callbacks[identifier] = f
        log("ReminderData: Registered " + identifier)
        return identifier

    def deregister_remove_callback(self, identifier: str) -> bool:
        log("ReminderData: Deregistering remove callback")
        if identifier in self._remove_callbacks:
            self._remove_callbacks.pop(identifier)
            return True
        else:
            logw("ReminderData: Callback not found")
            return False

    def remove_reminder(self, r_id: str) -> bool:
        log("ReminderData: Removing reminder " + r_id)
        if r_id in self._db_reminders:
            reminder = self._db_reminders[r_id]
            self._db_reminders.pop(r_id)
            self._reminders.remove(reminder)
            log("ReminderData: Removed " + r_id)
            log("ReminderData: Executing remove callbacks")
            for f in self._remove_callbacks.values():
                f(r_id)
            return True
        else:
            logw("ReminderData: Reminder not found")
            return False

    def get_reminder(self, r_id: str) -> Union[tuple, NoReturn]:
        log("ReminderData: Getting reminder " + r_id)
        if r_id in self._db_reminders:
            return self._db_reminders[r_id]
        else:
            logw("ReminderData: Reminder not found")

    def get_all_reminders(self) -> list:
        log("ReminderData: Getting all reminders")
        return self._reminders

    def save(self):
        log("ReminderData: Saving...")
        try:
            print(self._db_reminders)
            print(self._reminders)

            with open(self._REMINDER_SAVEFILE, 'wb') as savefile:
                pickle.dump(self._db_reminders, savefile)
        except:
            import traceback
            traceback.print_exc()
        self._autosave()

    def load(self):
        log("ReminderData: Loading data")
        if exists(self._REMINDER_SAVEFILE):
            log("ReminderData: Data found, loading...")
            with open(self._REMINDER_SAVEFILE, 'rb') as savefile:
                saved = pickle.load(savefile)
                self._db_reminders = saved
                self._reminders = list(self._db_reminders.values())
                log("Reminder data: Found " + str(len(self._reminders)) + " reminders")
                self._sort()

    def get_seconds_to(self, r_id: str) -> float:
        log("ReminderData: Getting seconds to " + r_id)
        rmndr = self.get_reminder(r_id)
        if rmndr is not None:
            ms = self._get_ms_time(rmndr[0], rmndr[1])
            return ms / 1000
        else:
            logw("ReminderData: Reminder not found")
            return -1

    @staticmethod
    def _get_ms_time(time, weekday: int) -> int:
        log("ReminderData: Getting ms to time")
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
        log("ReminderData: Got " + str(delta_ms) + " ms")
        return delta_ms

    def jsonify(self) -> str:
        log("ReminderData: JSONifying")
        rec_list = []
        for reminder in self._reminders:
            ms = self._get_ms_time(reminder[0], reminder[1])
            concept = reminder[2]
            r_dict = {'tiempo': ms, 'sonido': concept}
            rec_list.append(r_dict)
        if len(rec_list) > 0:
            json_dict = {'recordatorios': rec_list}
            return json.dumps(json_dict)
        else:
            return None

    def jsonify_id(self) -> str:
        log("IDReminderData: JSONifying")
        rec_list = []
        for reminder in self._reminders:
             #ms = self._get_ms_time(reminder[0], reminder[1])
            concept = reminder[2]
            #pasar time a ms
            r_dict = {"tiempo": (reminder[0].hour*1000*60*60 + reminder[0].minute*60*1000) , "dia": reminder[1],  "sonido": concept, "id": reminder[3] }
            rec_list.append(r_dict)
        json_dict = {'recordatorios': rec_list}
        return json.dumps(json_dict)
       
