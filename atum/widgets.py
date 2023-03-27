from collections import namedtuple
import curses

CommandListEntry = namedtuple("CommandListEntry", ["name", "fn"])


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
