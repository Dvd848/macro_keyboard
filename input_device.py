import fcntl
from typing import Callable
import ctypes
import linux_input

class InputDevice():
    def __init__(self, device_path: str):
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
        res = fcntl.ioctl(self._fd, linux_input.EVIOCGRAB, int(do_grab))
        if res < 0:
                raise OSError(-res)

    def loop_events(self, callback: Callable[[linux_input.struct_input_event], None]) -> None:
        while event := self._fd.read(ctypes.sizeof(linux_input.struct_input_event)):

            # https://stackoverflow.com/questions/38197517/
            # Note: type = EV_SYN, code = SYN_REPORT (0,0), is a synchronization event.
            # It means that at this point, the input event state has been completely updated.

            # You receive zero or more input records, followed by a type = EV_SYN, code = SYN_REPORT (0,0), 
            #  for events that happened "at the same time".


            input_event = linux_input.struct_input_event.from_buffer_copy(event)
            callback(input_event)
        

