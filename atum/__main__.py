from atum.tracker import workclock
import argparse

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(
        title="Work clock",
    )
    clock_in_parser = subparsers.add_parser("clin", help="clock in work")
    clock_in_parser.set_defaults(func=workclock.clock_in)
    reset_clock_parser = subparsers.add_parser("rclock", help="reset work clock")
    reset_clock_parser.set_defaults(func=workclock.reset_clock)
    status_clock_parser = subparsers.add_parser("status", help="show status of work clock")
    def print_status():
        print(workclock.status)
    status_clock_parser.set_defaults(func=print_status)
    new_args = parser.parse_args()
    new_args.func()
