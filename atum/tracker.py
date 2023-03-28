from dataclasses import dataclass
from datetime import datetime, timedelta
import shelve
import sys
import os


class WorkClock:
    def __init__(self, config_file_name: str = "AtumWorkClock.muta"):
        self.config_file_name = config_file_name
        self.config_file_path = os.path.join(
            sys.modules["atum"].__path__[0], config_file_name
        )
        self.is_clocked_in = False
        self._sync_db()

    def _sync_db(self):
        with shelve.open(self.config_file_path) as db_file:
            if "start_time" in db_file:
                # TODO Check if we actually finished work
                self.is_clocked_in = True
                self.start_time = db_file["start_time"]
                self.expected_end_time = db_file["expected_end_time"]

                time_delta = self.expected_end_time - self.start_time
                if time_delta.days < 0:
                    self.is_clocked_in = False
                    del db_file["start_time"]
                    del db_file["expected_end_time"]

    def clock_in(self, work_hours_and_minutes) -> str:
        if self.is_clocked_in:
            return f"Clocked in since {self.start_time}"

        time_clocked_in = datetime.now()
        parsed_time = datetime.strptime(work_hours_and_minutes, "%H:%M")
        with shelve.open(self.config_file_path) as db_file:
            db_file["start_time"] = time_clocked_in
            db_file["expected_end_time"] = time_clocked_in + timedelta(
                hours=parsed_time.hour, minutes=parsed_time.minute
            )

        self._sync_db()
        return f"Clocked in at {time_clocked_in}"

    def take_break(self, minutes: int) -> str:
        if not self.is_clocked_in:
            return "Not clocked in"

        with shelve.open(self.config_file_path) as db_file:
            old_time = db_file["expected_end_time"]
            db_file["expected_end_time"] += timedelta(minutes=minutes)
            self.expected_end_time = db_file["expected_end_time"]

        self._sync_db()
        return f"Break for {minutes}, expected to end work at: {self.expected_end_time}. was {old_time}"

    @property
    def status(self) -> tuple[str, str, str] | None:
        self._sync_db()
        if not self.is_clocked_in:
            return
        time_delta = self.expected_end_time - datetime.now()
        # if time_delta.days < 0:
        #     self.reset_clock()
        #     return f"You're done for today!"
        # return f"Clocked in at: {self.start_time.strftime('%A %I:%M:%S %p')}. Expected to end: {self.expected_end_time.strftime('%A %I:%M:%S %p')}. Remaining {str(time_delta).partition('.')[0]}"
        return (
            self.start_time.strftime("%A %I:%M:%S %p"),
            self.expected_end_time.strftime("%A %I:%M:%S %p"),
            str(time_delta).partition(".")[0],
        )

    def reset_clock(self) -> str:
        if not self.is_clocked_in:
            return "Not clocked in"

        self.is_clocked_in = False
        with shelve.open(self.config_file_path) as db_file:
            del db_file["start_time"]
            del db_file["expected_end_time"]

        self._sync_db()

        return "Clock reset"


workclock = WorkClock()
