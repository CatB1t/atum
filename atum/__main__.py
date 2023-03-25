import curses
from collections import namedtuple
from atum.tracker import workclock
from curses import wrapper

CmdListEntry = namedtuple("CmdListEntry", ["name", "fn"])

command_list = [CmdListEntry("Clock In", workclock.clock_in), 
                CmdListEntry("Reset Clock", workclock.reset_clock)]

def _main(stdscr: curses.window):
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    GREEN_AND_BLACK = curses.color_pair(1)
    # Show status
    status_window = stdscr.subwin(5, 100, 0, 0)
    status_window.box()
    status_window.addstr(0, 2, "Status")
    status_pad = stdscr.subpad(1, 97, 2, 2)
    if workclock.is_clocked_in:
        status_color = curses.COLOR_GREEN
    else:
        status_color = curses.COLOR_RED
    curses.init_pair(2, status_color, curses.COLOR_BLACK)
    status_pad.addstr(0, 0, workclock.status, curses.color_pair(2))
    status_pad.refresh()

    # Show Commands 
    commands_window = stdscr.subwin(5, 20, 5, 0) 
    cursor_pos = 0

    commands_window.addch(cursor_pos, 0, '>', GREEN_AND_BLACK)
    for i, item in enumerate(command_list):
        commands_window.addstr(i, 2, item.name)

    stdscr.nodelay(True)
    while True:
        status_pad.erase()
        if workclock.is_clocked_in:
            status_color = curses.COLOR_GREEN
        else:
            status_color = curses.COLOR_RED
        curses.init_pair(2, status_color, curses.COLOR_BLACK)
        status_pad.addstr(0, 0, workclock.status, curses.color_pair(2))
        status_pad.refresh()

        try:
            usr_input = stdscr.getkey().lower()
        except Exception as e:
            pass
        else:
            if usr_input.lower() == 'q':
                raise SystemExit
            elif usr_input == "\n": # Enter
                command_list[cursor_pos].fn()
            elif usr_input == 'w' or usr_input == 'key_up':
                commands_window.addch(cursor_pos, 0, ' ')
                if cursor_pos > 0:
                    cursor_pos -= 1
            elif usr_input == 's' or usr_input == 'key_down':
                commands_window.addch(cursor_pos, 0, ' ')
                if cursor_pos < len(command_list) - 1:
                    cursor_pos += 1
            
            commands_window.addch(cursor_pos, 0, '>', GREEN_AND_BLACK)
            commands_window.refresh()

def main():
    wrapper(_main)
