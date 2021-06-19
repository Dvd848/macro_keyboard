#!/usr/bin/env python3

from input_device import linux_input, InputDevice
from linux_input import struct_input_event, EventType, KeyEvent, Keys
from typing import Callable, List, Dict

import json
import subprocess
import os, pwd, grp
import argparse
import enum

class Commands(enum.Enum):
    LIST = "list"
    RUN  = "run"


# https://stackoverflow.com/questions/2699907/
def drop_privileges(uid_name = 'nobody', gid_name = 'nogroup'):
    if os.getuid() != 0:
        # We're not root
        return

    # Get the uid/gid from the name
    running_uid = pwd.getpwnam(uid_name).pw_uid
    running_gid = grp.getgrnam(gid_name).gr_gid

    # Remove group privileges
    os.setgroups([])

    # Try setting the new uid/gid
    os.setgid(running_gid)
    os.setuid(running_uid)

    # Ensure a very conservative umask
    os.umask(0o022)

def list_devices():
    print("The following devices are connected:")
    for device in os.listdir("/dev/input/by-id/"):
        print(f" (-) {device}")


def get_action_mapping(config_file: str) -> Dict[Keys, List[str]]:
    action_mapping = {}

    with open(config_file) as f:
        config = json.load(f)
        for item in config["ActionMapping"]:
            action_mapping[Keys[item["KeyCode"]]] = item["Action"]

    return action_mapping

def print_keystrokes(device_path: str) -> None:

    def handle_events(input_event: struct_input_event):
        if input_event.type != EventType.EV_KEY.value:
            return

        if input_event.value != KeyEvent.KEY_UP.value:
            return

        print(f"\nReceived keystroke: {Keys(input_event.code)}")

    run(device_path, False, handle_events)

def run_macro_keypad(device_path: str, action_mapping: Dict[Keys, List[str]]) -> None:

    def handle_events(input_event: struct_input_event):
        if input_event.type != EventType.EV_KEY.value:
            return

        if input_event.value != KeyEvent.KEY_UP.value:
            return

        key_code = linux_input.Keys(input_event.code)

        if key_code in action_mapping:
            print("Running command:\n{}".format(action_mapping[key_code]))
            subprocess.run(action_mapping[key_code])
            print("\nDone")
            print("-" * 20)
        

    run(device_path, True, handle_events)

def run(device_path: str, grab_device: bool, handler: Callable[[struct_input_event], None]) -> None:
    with InputDevice(device_path) as device:
        drop_privileges()
        assert(os.getresuid() != (0, 0, 0))

        print(f"Connected to device '{device.name}'")
        if grab_device:
            device.grab(True)

        device.loop_events(handler)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='A program to utilize a dedicated keyboard as a macro keyboard')

    subparsers = parser.add_subparsers(dest='command', required = True, title='subcommands',
                                       description='Valid subcommands')
    # A list command
    list_parser = subparsers.add_parser(Commands.LIST.value, help='List the devices under /dev/input/by-id/')

    # A run command
    run_parser = subparsers.add_parser(Commands.RUN.value, help='Attach to keyboard device and handle keystrokes')
    run_parser.add_argument('-d', '--device', action='store', help="The device path to connect to", required = True)
    run_action = run_parser.add_mutually_exclusive_group(required = True)
    run_action.add_argument('-p', '--print-keystrokes', action='store_true', help="Interactively print the user keystrokes")
    run_action.add_argument('-m', '--macro', action='store', type=str, metavar=('CONFIG_FILE'), help="Execute macros with the given configuration file")

    args = parser.parse_args()

    if args.command == Commands.LIST.value:
        list_devices()
    elif args.command == Commands.RUN.value:
        if args.print_keystrokes:
            print_keystrokes(args.device)
        elif args.macro:
            run_macro_keypad(args.device, get_action_mapping(args.macro))
