import curses
from collections import namedtuple
from curses import panel, textpad

CommandListEntry = namedtuple("CommandListEntry", ["name", "fn"])


class MainInputBox:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "instance"):
            cls.instance = super(MainInputBox, cls).__new__(cls)
        return cls.instance

    def __init__(self, stdscr: curses.window):
        self.main_window = stdscr
        ncols, nlines = 90, 1
        max_y, max_x = self.main_window.getmaxyx()
        y_center, x_center = max_y // 2, max_x // 2
        uly = y_center - nlines // 2
        lry = y_center + nlines // 2
        ulx = x_center - ncols // 2
        lrx = x_center + ncols // 2
        self.win = curses.newwin(lry - uly + 3, lrx - ulx - 1, uly, ulx)
        self.win.box()
        self._panel = panel.new_panel(self.win)
        self.textpad_win = self.win.subwin(
            lry - uly + 1, lrx - ulx - 3, uly + 1, ulx + 1
        )
        self.textpad_obj = textpad.Textbox(self.textpad_win)

    def get_input(self, prompt, default_value):
        if self._panel.hidden():
            self.textpad_win.clear()
            self._panel.show()
        self.win.box()
        self.win.addstr(0, 2, prompt)
        self.textpad_win.addstr(default_value)
        self.textpad_win.move(0, 0)
        curses.curs_set(True)
        self._panel.window().refresh()
        self.main_window.refresh()
        self.textpad_obj.edit()
        self._panel.hide()
        panel.update_panels()
        self.main_window.refresh()
        curses.curs_set(False)
        return self.textpad_obj.gather().strip()


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
