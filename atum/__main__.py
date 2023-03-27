import curses
from atum.tracker import workclock
from atum.tasks import task_tracker
from .widgets import CommandList, CommandListEntry, MainInputBox
from curses import wrapper


def _main(stdscr: curses.window):
    curses.curs_set(0)

    # Show status
    status_window = stdscr.subwin(7, 100, 0, 0)
    status_window.box()
    status_window.addstr(0, 2, "Status")
    status_pad = stdscr.subpad(3, 97, 2, 2)

    # Show Commands
    input_box = MainInputBox()

    def take_break():
        usr_input = int(input_box.get_input("15"))
        workclock.take_break(usr_input)

    def clock_in_with_time():
        usr_input = input_box.get_input("8:00")
        workclock.clock_in(usr_input)

    def start_task_input():
        usr_input = input_box.get_input("")
        task_tracker.start_task(usr_input)

    command_list = [
        CommandListEntry("Start Task", start_task_input),
        CommandListEntry("End Task", task_tracker.end_task),
        # CommandListEntry("Show Tasks", None),
        CommandListEntry("Take a break", take_break),
        CommandListEntry("Clock In", clock_in_with_time),
        CommandListEntry("Reset Clock", workclock.reset_clock),
    ]

    main_commands = CommandList(stdscr, 7, 0, command_list)
    stdscr.nodelay(True)
    while True:
        status_pad.erase()
        if workclock.is_clocked_in:
            status_color = curses.COLOR_GREEN
        else:
            status_color = curses.COLOR_RED
        curses.init_pair(2, status_color, curses.COLOR_BLACK)
        status_pad.addstr(0, 0, workclock.status, curses.color_pair(2))
        status_pad.addstr(
            1,
            0,
            f"Current task: {task_tracker.current_task_name}",
            curses.color_pair(2),
        )
        status_pad.addstr(
            2,
            0,
            f"Been working on task for: {task_tracker.time_on_task}",
            curses.color_pair(2),
        )
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
