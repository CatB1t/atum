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
        self.is_on_break = False
        self.break_duration = 0
        self.break_started_at = None
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

            if "is_on_break" in db_file:
                self.is_on_break = True
                self.break_duration = db_file["break_duration"]
                self.break_started_at = db_file["break_started_at"]
            else:
                self.is_on_break = False
                self.break_duration = 0
                self.break_started_at = None

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

    def take_break(self, minutes: int) -> None:
        if not self.is_clocked_in or self.is_on_break:
            return

        self.break_duration = timedelta(minutes=minutes)
        self.is_on_break = True
        self.expected_end_time += self.break_duration

        with shelve.open(self.config_file_path) as db_file:
            db_file["expected_end_time"] = self.expected_end_time
            db_file["is_on_break"] = True
            db_file["break_duration"] = self.break_duration
            db_file["break_started_at"] = datetime.now()

        self._sync_db()

    @property
    def status(self) -> tuple[str, str, str] | None:
        self._sync_db()
        if not self.is_clocked_in:
            return
        time_delta = self.expected_end_time - datetime.now()
        if time_delta.days < 0:
            self.reset_clock()
            return
        return (
            self.start_time.strftime("%A %I:%M:%S %p"),
            self.expected_end_time.strftime("%A %I:%M:%S %p"),
            str(time_delta).partition(".")[0],
        )

    @property
    def remaining_break_duration(self):
        if not self.is_on_break:
            return
        remainig_duration = self.break_duration - (
            datetime.now() - self.break_started_at
        )
        ret = f"{str(self.break_duration - (datetime.now() - self.break_started_at)).partition('.')[0]}"
        if remainig_duration.days < 0:
            with shelve.open(self.config_file_path) as db_file:
                del db_file["is_on_break"]
                del db_file["break_duration"]
                del db_file["break_started_at"]
        self._sync_db()
        return ret

    def cancel_break(self):
        if not self.is_on_break:
            return

        remaining_from_break = self.break_duration - (
            datetime.now() - self.break_started_at
        )
        self.expected_end_time -= remaining_from_break

        with shelve.open(self.config_file_path) as db_file:
            db_file["expected_end_time"] = self.expected_end_time
            del db_file["is_on_break"]
            del db_file["break_duration"]
            del db_file["break_started_at"]

        self._sync_db()
        return remaining_from_break

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
