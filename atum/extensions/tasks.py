class _Task:
    def __init__(self, name: str):
        self.name = name
        self.sub_tasks = []

    def add_description(self, desc: str):
        self.desc = desc

    def pause(self):
        pass

    def end(self):
        pass


class Tasks:
    def __init__(self):
        self.current_task = None
        self.tasks = []
