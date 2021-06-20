# Macro Keypad

This is a mini-project to transform a Numeric Keypad (although any keyboard should work as well) into a macro-keypad, executing predefined commands when different keys are pressed.

The setup just requires a Linux machine (with the ability to run as root) and an extra keyboard. 

The script opens a handle to the requested keyboard and "grabs" it (blocking any other application from receiving keystrokes). It then waits for keystrokes and executes a predefined command once a matching keystroke arrives.

#### Background

I use this project to allow a preschooler to play a few predefined songs on demand, by mapping them to the keypad keys. The script runs as a service on a Raspberry PI, and upon identifying a keystroke, sends a command to play the mapped song over JSON-RPC to a remote Kodi setup.

## Usage

### 1. Identify the keyboard device path

One way to do this is to list `/dev/input/by-id/`:

```console
$ ls -al /dev/input/by-id/
total 0
drwxr-xr-x 2 root root  80 Jun 20 14:27 .
drwxr-xr-x 4 root root 160 Jun 20 14:27 ..
lrwxrwxrwx 1 root root   9 Jun 20 14:27 usb-04d9_1203-event-if01 -> ../event1
lrwxrwxrwx 1 root root   9 Jun 20 14:27 usb-04d9_1203-event-kbd -> ../event0
```

Another way is to request the script to list devices under `/dev/input/by-id/`:

```console
$ python3 macro_keypad.py list
The following devices are connected:
 (-) usb-04d9_1203-event-if01
 (-) usb-04d9_1203-event-kbd
```

If multiple keyboards are connected, it's possible to identify the requested one by comparing the output when the keyboard is connected and disconnected.

### 2. Take the keyboard to a test run

Run the script in "print-only" mode, hit some keys and verify that the script identifies them.

For example:

```console
$ python3 macro_keypad.py run -d /dev/input/by-id/usb-04d9_1203-event-kbd -p
Connected to device 'HID 04d9:1203'

Received keystroke: Keys.KEY_KP1

Received keystroke: Keys.KEY_KP2

Received keystroke: Keys.KEY_KP3
^C
Quitting...
```

### 3. Create the configuration file

The configuration file is a JSON file with a mapping of keys to actions.

For example:

```json
{
    "ActionMapping": [
        {
            "Name": "Stop",
            "KeyCode": "KEY_KP0",
            "Action": ["curl", "192.168.1.50:8080/jsonrpc", "-X", "POST", "--header", "Content-Type: application/json",
                       "--data", "{\"method\": \"Player.Stop\", \"id\": 44, \"jsonrpc\": \"2.0\", \"params\": { \"playerid\": 0 }}"]
        },
        {
            "KeyCode": "KEY_KP9",
            "Action": ["whoami"]
        }
    ]
}
```

The first command in the example is run when the '`0`' is pressed. It performs a JSON-RPC command to a remote Kodi setup to stop the current song from playing.

The second command simply calls `whoami`, and it runs with '`9`' is hit.

Since my main usage is communicating with Kodi over JSON-RPC, a `kodi.py` wrapper for this cause is provided under `plugins`.

### 4. Run the script

Note that you must run the script as root in order to open a handle to the keyboard. The script attempts to drop privileges after opening the handle.

An example for running with the above configuration and hitting `9`.

```console
$ python3 macro_keypad.py run -d /dev/input/by-id/usb-04d9_1203-event-kbd -m config.json
Connected to device 'HID 04d9:1203'
Running command:
['whoami']
pi
```

### 5. Configure the script to run on startup

This is optional. 

There are many ways to do this. Using `systemd` was tested and worked well.


## Troubleshooting

A few things that should be attempted if things don't go as expected.

### 1. Directly read from `/dev/input/`

Run the following command (change the device path to your own):

```console
$ cat /dev/input/by-id/usb-04d9_1203-event-kbd
```

Then, press a few keys on the keyboard. If nothing appears on the screen, some other program might be grabbing the keyboard.

### 2. Check if another program is grabbing the keyboard

If another program is grabbing the keyboard, keystrokes won't arrive to our script.

You can try running `evtest`:

```console
$ evtest
No device specified, trying to scan all of /dev/input/event*
Available devices:
/dev/input/event0:      HID 04d9:1203
/dev/input/event1:      HID 04d9:1203
Select the device event number [0-1]: 0
Input driver version is 1.0.1
Input device ID: bus 0x3 vendor 0x4d9 product 0x1203 version 0x111
Input device name: "HID 04d9:1203"
Supported events:
    Event type 0 (EV_SYN)
    ...
    Event code 2 (LED_SCROLLL) state 0
Key repeat handling:
  Repeat type 20 (EV_REP)
    Repeat code 0 (REP_DELAY)
      Value    400
    Repeat code 1 (REP_PERIOD)
      Value     80
Properties:
Testing ... (interrupt to exit)
***********************************************
  This device is grabbed by another process.
  No events are available to evtest while the
  other grab is active.
  In most cases, this is caused by an X driver,
  try VT-switching and re-run evtest again.
  Run the following command to see processes with
  an open fd on this device
 "fuser -v /dev/input/event0"
***********************************************
```

The output will tell you if the process is grabbed. It suggests to run `fuser` to see who is grabbing it:

```console
$ fuser  /dev/input/event0
421
$ fuser  /dev/input/by-id/usb-04d9_1203-event-kbd
421
```

We can then use `top` or `ps` to identify the process:

```console
$ top -p 421
  PID  PPID USER     STAT   VSZ %VSZ CPU %CPU COMMAND
  421   417 root     S     532m 72.4   1  2.9 /usr/lib/kodi/kodi.bin --standalone -fs --lircdev /run/lirc/lircd
```

Causing the program to stop grabbing the device is out of scope though (and usually not trivial).