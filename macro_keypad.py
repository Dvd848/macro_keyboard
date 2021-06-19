#!/usr/bin/env python3

from input_device import linux_input, InputDevice
from linux_input import struct_input_event, EventType, KeyEvent, Keys
import json
import subprocess
import os, pwd, grp


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


def handle_events(input_event: struct_input_event):

    if input_event.type != EventType.EV_KEY.value:
        return

    if input_event.value != KeyEvent.KEY_UP.value:
        return

    key_code = linux_input.Keys(input_event.code)
    print(f"Received key: {key_code}")

    try:
        print("-" * 6)
        subprocess.run(action_mapping[key_code])
        print(f"\n{'-' * 6}")
    except KeyError:
        pass


action_mapping = {}

with open("config.json") as f:
    config = json.load(f)
    for item in config["ActionMapping"]:
        action_mapping[Keys[item["KeyCode"]]] = item["Action"]

print(action_mapping)

with InputDevice("/dev/input/by-id/usb-04d9_1203-event-kbd") as device:
    drop_privileges()
    assert(os.getresuid() != (0, 0, 0))

    print(f"Connected to device '{device.name}'")
    device.grab(True)

    device.loop_events(handle_events)