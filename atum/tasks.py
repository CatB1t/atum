import sys
import os
import json

from datetime import datetime, timedelta
from collections import namedtuple

TaskRecord = namedtuple("TaskRecord", ["start_time", "time"])


class DatetimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, timedelta):
            return str(obj).partition(".")[0]
        return json.JSONEncoder.default(self, obj)


class TaskTracker:
    def __init__(self, tasks_file="tasks.json"):
        self.tasks_file_name = tasks_file
        self.absolute_tasks_file_path = os.path.join(
            sys.modules["atum"].__path__[0], self.tasks_file_name
        )
        self.current_task_start_time = None
        self.current_task = None
        self.current_task_name = None
        self.tasks = {}
        if os.path.exists(self.absolute_tasks_file_path):
            with open(self.absolute_tasks_file_path) as json_file:
                data_dict = json.load(json_file)
                for key, value in data_dict["tasks"].items():
                    self.tasks[key] = TaskRecord(
                        datetime.fromisoformat(value[0]), value[1]
                    )
                self.current_task_name = data_dict["current_task_name"]
                if self.current_task_name is not None:
                    self.current_task = self.tasks[self.current_task_name]
        else:
            self._write_task_records()

    def _write_task_records(self):
        with open(self.absolute_tasks_file_path, "w") as json_file:
            json.dump(
                {"current_task_name": self.current_task_name, "tasks": self.tasks},
                json_file,
                cls=DatetimeEncoder,
            )

    @property
    def time_on_task(self):
        if self.current_task is None:
            return -1

        time_delta = datetime.now() - self.current_task.start_time
        return str(time_delta).partition(".")[0]

    def start_task(self, name, try_override=False):
        if self.current_task is not None:
            return

        self.current_task = TaskRecord(datetime.now(), None)
        self.current_task_name = name
        self.tasks[name] = self.current_task
        self._write_task_records()

    def end_task(self):
        if self.current_task is None:
            return

        start_time = self.current_task.start_time
        name = self.current_task_name
        self.current_task = TaskRecord(start_time, datetime.now() - start_time)
        self.tasks[self.current_task_name] = self.current_task
        self.current_task = None
        self.current_task_name = None
        self._write_task_records()

    def get_tasks(self):
        ret = ""
        for key, value in self.tasks.items():
            ret += f"Name: {key}, Start time: {value.start_time.strftime('%H:%M:%S')}, "
            f"Time taken: {value.time}\n"
        return ret

    def clear_tasks(self):
        self.tasks = {}
        self.current_task = None
        self.current_task_name = None
        if os.path.exists(self.absolute_tasks_file_path):
            os.remove(self.absolute_tasks_file_path)


task_tracker = TaskTracker()
