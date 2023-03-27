from collections import namedtuple
import curses

CommandListEntry = namedtuple("CommandListEntry", ["name", "fn"])


class MainInputBox:
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(MainInputBox, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.window = curses.newwin(1, curses.COLS, curses.LINES - 1, 0)
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
        self.WHITE_AND_BLACK = curses.color_pair(1)
        self.BLACK_AND_WHITE = curses.color_pair(2)

    def get_input(self, default_value):
        curses.curs_set(True)
        curses.echo(True)
        self.window.bkgd(" ", self.WHITE_AND_BLACK)
        self.window.insstr(0, 0, default_value)
        self.window.refresh()

        str_input = self.window.getstr(0, 0).decode(self.window.encoding)

        curses.curs_set(False)
        curses.echo(False)
        self.window.erase()
        self.window.bkgd(" ", self.BLACK_AND_WHITE)
        self.window.refresh()

        if str_input == "":
            return default_value
        return str_input


class CommandList:
    def __init__(self, parent_window: curses.window, pos_x, pos_y, items):
        self.current_cursor_pos = 0
        self.items = items
        requried_lines = len(items)
        self.window = parent_window.subwin(requried_lines, 100, pos_x, pos_y)

    def handle(self, key):
        if key == "\n":  # Enter
            self.items[self.current_cursor_pos].fn()
        elif key == "w" or key == "key_up":
            if self.current_cursor_pos > 0:
                self.current_cursor_pos -= 1
        elif key == "s" or key == "key_down":
            if self.current_cursor_pos < len(self.items) - 1:
                self.current_cursor_pos += 1

    def show(self):
        self.window.erase()
        self.window.addch(self.current_cursor_pos, 0, ">")

        for i, item in enumerate(self.items):
            self.window.addstr(i, 2, item.name)

        self.window.refresh()
