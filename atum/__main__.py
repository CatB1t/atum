import curses
from atum.tracker import workclock
from atum.tasks import task_tracker
from .widgets import CommandList, CommandListEntry, MainInputBox
from curses import wrapper


print_tasks = False
should_exit_atum = False


def _main(stdscr: curses.window):
    curses.curs_set(0)

    # Setup status colors
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)
    GREEN_AND_BLACK = curses.color_pair(3)
    RED_AND_BLACK = curses.color_pair(4)

    # Show status
    STATUS_BOX_SIZE_Y = 13
    STATUS_BOX_SIZE_X = 70
    status_window = stdscr.subwin(STATUS_BOX_SIZE_Y, STATUS_BOX_SIZE_X, 0, 0)
    status_window.box()
    status_window.addstr(0, 2, "Status")
    WORK_STATUS_BOX_SIZE_Y = 3
    TASK_STATUS_BOX_SIZE_Y = 4
    status_window.hline(WORK_STATUS_BOX_SIZE_Y + 3, 1, "-", STATUS_BOX_SIZE_X - 2)
    work_status_pad = stdscr.subpad(WORK_STATUS_BOX_SIZE_Y, STATUS_BOX_SIZE_X - 3, 2, 2)
    task_status_pad = stdscr.subpad(
        TASK_STATUS_BOX_SIZE_Y, STATUS_BOX_SIZE_X - 3, 4 + WORK_STATUS_BOX_SIZE_Y, 2
    )

    # Show Commands
    input_box = MainInputBox(stdscr)

    def take_break():
        usr_input = int(input_box.get_input("Enter break time (in minutes)", "15"))
        workclock.take_break(usr_input)

    def clock_in_with_time():
        usr_input = input_box.get_input("Enter working time (H:M)", "8:00")
        workclock.clock_in(usr_input)

    def start_task_input():
        usr_input = input_box.get_input("Enter task title:", "")
        task_tracker.start_task(usr_input)

    def print_tasks_and_exit():
        global print_tasks, should_exit_atum
        print_tasks = True
        should_exit_atum = True

    command_list = [
        CommandListEntry("Start Task", start_task_input),
        CommandListEntry("End Task", task_tracker.end_task),
        CommandListEntry("Show Tasks", print_tasks_and_exit),
        CommandListEntry("Clear Tasks", task_tracker.clear_tasks),
        CommandListEntry("Clock In", clock_in_with_time),
        CommandListEntry("Take a break", take_break),
        CommandListEntry("Cancel Break", workclock.cancel_break),
        CommandListEntry("Reset Clock", workclock.reset_clock),
    ]

    main_commands = CommandList(stdscr, STATUS_BOX_SIZE_Y, 0, command_list)
    stdscr.nodelay(True)

    while not should_exit_atum:
        work_status_pad.erase()
        task_status_pad.erase()

        # Work clock status ##
        work_status_pad.addstr(0, 0, "\u2728 Work Status")

        if workclock.is_clocked_in:
            work_status_color = GREEN_AND_BLACK
        else:
            work_status_color = RED_AND_BLACK

        if workclock.is_clocked_in:
            if workclock.is_on_break:
                work_status_pad.addstr(
                    1,
                    0,
                    f"On break. Remaining {workclock.remaining_break_duration}",
                    work_status_color,
                )
            else:
                start_time, end_time, remaining_time = workclock.status
                work_status_pad.addstr(
                    1,
                    0,
                    f"Clocked in at {start_time}. Finish at {end_time}",
                    work_status_color,
                )
                work_status_pad.addstr(
                    2, 0, f"Remaining work hours: {remaining_time}", work_status_color
                )
            work_status_pad.refresh()
        else:
            work_status_pad.addstr(1, 0, "Not on duty.", work_status_color)
        # End work clock status ##

        # Current task status ##
        task_status_pad.addstr(1, 0, f"\U0001F4D7 Tasks Status")
        if task_tracker.current_task is None:
            task_status_pad.addstr(2, 0, "No active task", RED_AND_BLACK)
        else:
            task_status_pad.addstr(
                2, 0, f"Current Task: {task_tracker.current_task_name}", GREEN_AND_BLACK
            )
            task_status_pad.addstr(
                3, 0, f"Time: {task_tracker.time_on_task}", GREEN_AND_BLACK
            )
        # End current task status ##

        work_status_pad.refresh()
        task_status_pad.refresh()
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

    curses.endwin()


def _postprocess():
    if print_tasks:
        print(task_tracker.get_tasks())


def main():
    wrapper(_main)
    _postprocess()
