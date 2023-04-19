from datetime import datetime, timedelta
from collections import namedtuple

RemainingTime = namedtuple("RemainingTime", "hours,minutes,seconds")


class Timer:
    def __init__(self, time: str, start_on_init: bool = True):
        """Create a new timer

        Args:
            time: Time in the format %H:%M:%S
            start_on_init: If true, start the timer after initialization. Defaults to True.
        """
        formatted_time = datetime.strptime(time, "%H:%M:%S")
        self.time = timedelta(
            hours=formatted_time.hour,
            minutes=formatted_time.minute,
            seconds=formatted_time.second,
        )
        if start_on_init:
            self.start()

    def start(self):
        """Start the timer"""
        self.expected_end = datetime.now() + self.time

    def pause(self):
        pass

    def unpause(self):
        pass

    def stop(self):
        """Stop the timer"""
        self.expected_end = datetime.now()

    @property
    def has_finished(self):
        """Returns True if timer is finished"""
        time_delta = self.expected_end - datetime.now()
        return time_delta.days < 0

    @property
    def remaining_time(self):
        """Return remaining hours, minutes, seconds"""
        if self.has_finished:
            return RemainingTime(0, 0, 0)
        time_delta = self.expected_end - datetime.now()
        return RemainingTime(
            time_delta.seconds // 3600,
            time_delta.seconds // 60,
            time_delta.seconds % 60,
        )

    @property
    def remaining_time_str(self) -> str:
        """Return remaining time in format %H:%M:%S"""
        unparsed_time = self.remaining_time
        return "%02d:%02d:%02d" % (
            unparsed_time.hours,
            unparsed_time.minutes,
            unparsed_time.seconds,
        )
