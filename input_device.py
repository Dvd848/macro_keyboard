"""Representation of an input device.

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
import fcntl
from typing import Callable
import ctypes
import linux_input

class InputDevice():
    """Representation of an input device.
    
    Implemented as a context manager.

    Example usage:

    >>> with InputDevice("/dev/input/by-id/my_device") as device:
    ...     print(device.name)
    """

    def __init__(self, device_path: str):
        """Initialize an input device.

        Args:
            device_path: 
                Path to the device, under "/dev/input/"
        """
        self._device_path = device_path
        self._fd = None
        self._name = None

    def __enter__(self):
        self._fd = open(self._device_path, "rb")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self._fd is not None:
            self._fd.close()
            self._fd = None

    @property
    def name(self) -> str:
        """Name of the device as reported by EVIOCGNAME."""

        if self._name is None:      
            buffer_length = 255
            name = (ctypes.c_char * buffer_length)()
            actual_length = fcntl.ioctl(self._fd, linux_input.EVIOCGNAME(buffer_length), name, True)
            if actual_length < 0:
                raise OSError(-actual_length)
            if name[actual_length - 1] == b'\x00':
                actual_length -= 1
            self._name = name[:actual_length].decode("ascii")
        return self._name

    def grab(self, do_grab: bool) -> None:
        """Grab the device for exclusive use (block input from arriving to other programs).

        Args:
            do_grab:
                True for grabbing the device for exclusive use, False for releasing the device.
        """
        res = fcntl.ioctl(self._fd, linux_input.EVIOCGRAB, int(do_grab))
        if res < 0:
            raise OSError(-res)

    def loop_events(self, callback: Callable[[linux_input.struct_input_event], None]) -> None:
        """Attach to the device, wait for incoming events and transfer them to the callback for handling.

        Args:
            callback:
                A callback to which incoming events are transferred to.
        """
        while event := self._fd.read(ctypes.sizeof(linux_input.struct_input_event)):

            # https://stackoverflow.com/questions/38197517/
            # Note: type = EV_SYN, code = SYN_REPORT (0,0), is a synchronization event.
            # It means that at this point, the input event state has been completely updated.

            # You receive zero or more input records, followed by a type = EV_SYN, code = SYN_REPORT (0,0), 
            #  for events that happened "at the same time".


            input_event = linux_input.struct_input_event.from_buffer_copy(event)
            callback(input_event)
        

