import curses
from atum.tracker import workclock
from .widgets import CommandList, CommandListEntry
from curses import wrapper


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
    command_list = [
        CommandListEntry("Clock In", workclock.clock_in),
        CommandListEntry("Reset Clock", workclock.reset_clock),
    ]

    main_commands = CommandList(stdscr, 5, 0, command_list)
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

        main_commands.show()
        try:
            usr_input = stdscr.getkey().lower()
        except Exception as e:
            pass
        else:
            if usr_input.lower() == "q":
                raise SystemExit
            else:
                main_commands.handle(usr_input)


def main():
    wrapper(_main)
