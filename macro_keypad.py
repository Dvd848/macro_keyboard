#!/usr/bin/env python3

"""A macro keypad (or keyboard) implementation.

This program allows you to attach to a specific keyboard and execute
custom predefined commands for each keystroke.
The keystrokes are captured by the program and not propagated to any additional 
program, turning the keyboard into a macro-only keyboard.

The commands are defined in a JSON configuration file provided to the program.
The KeyCode is a name of a key from linux_input.Keys.
The Action is an array of commands compatible with subprocess.run.
Example:
    {
        "ActionMapping": [
            {
                "KeyCode": "KEY_KP1",
                "Action": ["whoami"]
            },
            {
                "KeyCode": "KEY_KP2",
                "Action": ["echo", "Hello World!"]
            }
        ]
    }

Sources:
    https://github.com/Dvd848/macro_keyboard

License:
    LGPL v2.1

    This library is free software; you can redistribute it and/or
    modify it under the terms of the GNU Lesser General Public
    License as published by the Free Software Foundation; either
    version 2.1 of the License, or (at your option) any later version.

    This library is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
    Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public
    License along with this library; if not, write to the Free Software
    Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

"""

from input_device import linux_input, InputDevice
from linux_input import struct_input_event, EventType, KeyEvent, Keys
from typing import Callable, List, Dict

import json
import subprocess
import os, pwd, grp
import argparse
import enum

def drop_privileges(uid_name = 'nobody', gid_name = 'nogroup'):
    """Drop privileges of current program in case it is running as root.

    Based on https://stackoverflow.com/questions/2699907/
    """
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
    """List devices under /dev/input/by-id/"""
    print("The following devices are connected:")
    for device in os.listdir("/dev/input/by-id/"):
        print(f" (-) {device}")


def get_action_mapping(config_file: str) -> Dict[Keys, List[str]]:
    """Translate action mapping from a file to a dictionary.

    Given a configuration file containing a mapping of keys to actions,
    read the file and return a dictionary of key -> action.
    The action is an array of commands, compatible with subprocess.run,
    For example: ["ls", "-l"].

    Args:
        config_str: Path to JSON configuration file.

    Returns:
        Dictionary of key -> action
    """
    action_mapping = {}

    with open(config_file) as f:
        config = json.load(f)
        for item in config["ActionMapping"]:
            action_mapping[Keys[item["KeyCode"]]] = item["Action"]

    return action_mapping

def print_keystrokes(device_path: str) -> None:
    """Callback to print keystrokes of a given device.
    
    Args:
        device_path: 
            Path to device.
    """
    def handle_events(input_event: struct_input_event):
        if input_event.type != EventType.EV_KEY.value:
            return

        if input_event.value != KeyEvent.KEY_UP.value:
            return

        print(f"\nReceived keystroke: {Keys(input_event.code)}")

    run(device_path, False, handle_events)

def run_macro_keypad(device_path: str, action_mapping: Dict[Keys, List[str]]) -> None:
    """Callback to execute commands from the given mapping for a given device.

    This function accepts a path to a device and a mapping of keys -> actions.
    It executes the appropriate action given the matching keystroke.
    
    Args:
        device_path: 
            Path to device.

        action_mapping:
            Mapping of key -> action.
    """
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
    """Attach to a given device and call the handler for every device event.

    Args:
        device_path:
            Path to the device.

        grab_device:
            True if keystrokes from the device should be blocked from arriving to other programs.

        handler:
            Callback to call for every event from the device.

    """
    try:
        with InputDevice(device_path) as device:
            drop_privileges() # Opening the device must be done as root, drop privileges after
            assert(os.getresuid() != (0, 0, 0))

            print(f"Connected to device '{device.name}'")
            if grab_device:
                device.grab(True)

            device.loop_events(handler)
    except PermissionError as e:
        raise PermissionError("Permission denied, are you running as root?") from e



if __name__ == "__main__":
    class Commands(enum.Enum):
        """Commands for argument parsing."""
        LIST = "list"
        RUN  = "run"

    parser = argparse.ArgumentParser(description = 'A program to utilize a dedicated keyboard as a macro keyboard')

    subparsers = parser.add_subparsers(dest = 'command', required = True, title = 'subcommands',
                                       description = 'Valid subcommands')
    # A "list" command
    list_parser = subparsers.add_parser(Commands.LIST.value, help = 'List the devices under /dev/input/by-id/')

    # A "run" command
    run_parser = subparsers.add_parser(Commands.RUN.value, help = 'Attach to keyboard device and handle keystrokes')
    run_parser.add_argument('-d', '--device', action = 'store', help = "The device path to connect to", required = True)
    run_action = run_parser.add_mutually_exclusive_group(required = True)
    run_action.add_argument('-p', '--print-keystrokes', action = 'store_true', help = "Interactively print the user keystrokes")
    run_action.add_argument('-m', '--macro', action = 'store', type = str, metavar = ('CONFIG_FILE'), 
                            help = "Execute macros with the given configuration file")

    args = parser.parse_args()

    try:
        if args.command == Commands.LIST.value:
            list_devices()
        elif args.command == Commands.RUN.value:
            if args.print_keystrokes:
                print_keystrokes(args.device)
            elif args.macro:
                run_macro_keypad(args.device, get_action_mapping(args.macro))
    except Exception as e:
        print(f"Error: {str(e)}")
    except KeyboardInterrupt:
        print ("\nQuitting...")

