import ctypes
import enum

from ioctl_opt import IOC, IOW, IOC_READ

EVIOCGNAME = lambda length: IOC(IOC_READ, ord('E'), 0x06, length)
EVIOCGRAB  = IOW(ord('E'), 0x90, ctypes.c_uint32)

class EventType(enum.Enum):
    EV_SYN       =   0x00
    EV_KEY       =   0x01
    EV_REL       =   0x02
    EV_ABS       =   0x03
    EV_MSC       =   0x04
    EV_SW        =   0x05
    EV_LED       =   0x11
    EV_SND       =   0x12
    EV_REP       =   0x14
    EV_FF        =   0x15
    EV_PWR       =   0x16
    EV_FF_STATUS =   0x17
    
class SynchronizationEvent(enum.Enum):
    SYN_REPORT    =  0
    SYN_CONFIG    =  1
    SYN_MT_REPORT =  2
    SYN_DROPPED   =  3
    
class MiscEvent(enum.Enum):
    MSC_SERIAL   =   0x00
    MSC_PULSELED =   0x01
    MSC_GESTURE  =   0x02
    MSC_RAW      =   0x03
    MSC_SCAN     =   0x04
    MSC_MAX      =   0x07
    
class Keys(enum.Enum):
    KEY_RESERVED = 0
    KEY_ESC = 1
    KEY_1 = 2
    KEY_2 = 3
    KEY_3 = 4
    KEY_4 = 5
    KEY_5 = 6
    KEY_6 = 7
    KEY_7 = 8
    KEY_8 = 9
    KEY_9 = 10
    KEY_0 = 11
    KEY_MINUS = 12
    KEY_EQUAL = 13
    KEY_BACKSPACE = 14
    KEY_TAB = 15
    KEY_Q = 16
    KEY_W = 17
    KEY_E = 18
    KEY_R = 19
    KEY_T = 20
    KEY_Y = 21
    KEY_U = 22
    KEY_I = 23
    KEY_O = 24
    KEY_P = 25
    KEY_LEFTBRACE = 26
    KEY_RIGHTBRACE = 27
    KEY_ENTER = 28
    KEY_LEFTCTRL = 29
    KEY_A = 30
    KEY_S = 31
    KEY_D = 32
    KEY_F = 33
    KEY_G = 34
    KEY_H = 35
    KEY_J = 36
    KEY_K = 37
    KEY_L = 38
    KEY_SEMICOLON = 39
    KEY_APOSTROPHE = 40
    KEY_GRAVE = 41
    KEY_LEFTSHIFT = 42
    KEY_BACKSLASH = 43
    KEY_Z = 44
    KEY_X = 45
    KEY_C = 46
    KEY_V = 47
    KEY_B = 48
    KEY_N = 49
    KEY_M = 50
    KEY_COMMA = 51
    KEY_DOT = 52
    KEY_SLASH = 53
    KEY_RIGHTSHIFT = 54
    KEY_KPASTERISK = 55
    KEY_LEFTALT = 56
    KEY_SPACE = 57
    KEY_CAPSLOCK = 58
    KEY_F1 = 59
    KEY_F2 = 60
    KEY_F3 = 61
    KEY_F4 = 62
    KEY_F5 = 63
    KEY_F6 = 64
    KEY_F7 = 65
    KEY_F8 = 66
    KEY_F9 = 67
    KEY_F10 = 68
    KEY_NUMLOCK = 69
    KEY_SCROLLLOCK = 70
    KEY_KP7 = 71
    KEY_KP8 = 72
    KEY_KP9 = 73
    KEY_KPMINUS = 74
    KEY_KP4 = 75
    KEY_KP5 = 76
    KEY_KP6 = 77
    KEY_KPPLUS = 78
    KEY_KP1 = 79
    KEY_KP2 = 80
    KEY_KP3 = 81
    KEY_KP0 = 82
    KEY_KPDOT = 83

    KEY_ZENKAKUHANKAKU = 85
    KEY_102ND = 86
    KEY_F11 = 87
    KEY_F12 = 88
    KEY_RO = 89
    KEY_KATAKANA = 90
    KEY_HIRAGANA = 91
    KEY_HENKAN = 92
    KEY_KATAKANAHIRAGANA = 93
    KEY_MUHENKAN = 94
    KEY_KPJPCOMMA = 95
    KEY_KPENTER = 96
    KEY_RIGHTCTRL = 97
    KEY_KPSLASH = 98
    KEY_SYSRQ = 99
    KEY_RIGHTALT = 100
    KEY_LINEFEED = 101
    KEY_HOME = 102
    KEY_UP = 103
    KEY_PAGEUP = 104
    KEY_LEFT = 105
    KEY_RIGHT = 106
    KEY_END = 107
    KEY_DOWN = 108
    KEY_PAGEDOWN = 109
    KEY_INSERT = 110
    KEY_DELETE = 111
    KEY_MACRO = 112
    KEY_MUTE = 113
    KEY_VOLUMEDOWN = 114
    KEY_VOLUMEUP = 115
    KEY_POWER = 116  # SC System Power Down
    KEY_KPEQUAL = 117
    KEY_KPPLUSMINUS = 118
    KEY_PAUSE = 119
    KEY_SCALE = 120  # AL Compiz Scale (Expose)

    KEY_KPCOMMA = 121
    KEY_HANGEUL = 122
    KEY_HANGUEL = KEY_HANGEUL
    KEY_HANJA = 123
    KEY_YEN = 124
    KEY_LEFTMETA = 125
    KEY_RIGHTMETA = 126
    KEY_COMPOSE = 127

    KEY_STOP = 128  # AC Stop
    KEY_AGAIN = 129
    KEY_PROPS = 130  # AC Properties
    KEY_UNDO = 131  # AC Undo
    KEY_FRONT = 132
    KEY_COPY = 133  # AC Copy
    KEY_OPEN = 134  # AC Open
    KEY_PASTE = 135  # AC Paste
    KEY_FIND = 136  # AC Search
    KEY_CUT = 137  # AC Cut
    KEY_HELP = 138  # AL Integrated Help Center
    KEY_MENU = 139  # Menu (show menu)
    KEY_CALC = 140  # AL Calculator
    KEY_SETUP = 141
    KEY_SLEEP = 142  # SC System Sleep
    KEY_WAKEUP = 143  # System Wake Up
    KEY_FILE = 144  # AL Local Machine Browser
    KEY_SENDFILE = 145
    KEY_DELETEFILE = 146
    KEY_XFER = 147
    KEY_PROG1 = 148
    KEY_PROG2 = 149
    KEY_WWW = 150  # AL Internet Browser
    KEY_MSDOS = 151
    KEY_COFFEE = 152  # AL Terminal Lock/Screensaver
    KEY_SCREENLOCK = KEY_COFFEE
    KEY_DIRECTION = 153
    KEY_CYCLEWINDOWS = 154
    KEY_MAIL = 155
    KEY_BOOKMARKS = 156  # AC Bookmarks
    KEY_COMPUTER = 157
    KEY_BACK = 158  # AC Back
    KEY_FORWARD = 159  # AC Forward
    KEY_CLOSECD = 160
    KEY_EJECTCD = 161
    KEY_EJECTCLOSECD = 162
    KEY_NEXTSONG = 163
    KEY_PLAYPAUSE = 164
    KEY_PREVIOUSSONG = 165
    KEY_STOPCD = 166
    KEY_RECORD = 167
    KEY_REWIND = 168
    KEY_PHONE = 169  # Media Select Telephone
    KEY_ISO = 170
    KEY_CONFIG = 171  # AL Consumer Control Configuration
    KEY_HOMEPAGE = 172  # AC Home
    KEY_REFRESH = 173  # AC Refresh
    KEY_EXIT = 174  # AC Exit
    KEY_MOVE = 175
    KEY_EDIT = 176
    KEY_SCROLLUP = 177
    KEY_SCROLLDOWN = 178
    KEY_KPLEFTPAREN = 179
    KEY_KPRIGHTPAREN = 180
    KEY_NEW = 181  # AC New
    KEY_REDO = 182  # AC Redo/Repeat

    KEY_F13 = 183
    KEY_F14 = 184
    KEY_F15 = 185
    KEY_F16 = 186
    KEY_F17 = 187
    KEY_F18 = 188
    KEY_F19 = 189
    KEY_F20 = 190
    KEY_F21 = 191
    KEY_F22 = 192
    KEY_F23 = 193
    KEY_F24 = 194

    KEY_PLAYCD = 200
    KEY_PAUSECD = 201
    KEY_PROG3 = 202
    KEY_PROG4 = 203
    KEY_DASHBOARD = 204  # AL Dashboard
    KEY_SUSPEND = 205
    KEY_CLOSE = 206  # AC Close
    KEY_PLAY = 207
    KEY_FASTFORWARD = 208
    KEY_BASSBOOST = 209
    KEY_PRINT = 210  # AC Print
    KEY_HP = 211
    KEY_CAMERA = 212
    KEY_SOUND = 213
    KEY_QUESTION = 214
    KEY_EMAIL = 215
    KEY_CHAT = 216
    KEY_SEARCH = 217
    KEY_CONNECT = 218
    KEY_FINANCE = 219  # AL Checkbook/Finance
    KEY_SPORT = 220
    KEY_SHOP = 221
    KEY_ALTERASE = 222
    KEY_CANCEL = 223  # AC Cancel
    KEY_BRIGHTNESSDOWN = 224
    KEY_BRIGHTNESSUP = 225
    KEY_MEDIA = 226

    KEY_SWITCHVIDEOMODE = 227  # Cycle between available video
    # outputs (Monitor/LCD/TV-out/etc)
    KEY_KBDILLUMTOGGLE = 228
    KEY_KBDILLUMDOWN = 229
    KEY_KBDILLUMUP = 230

    KEY_SEND = 231  # AC Send
    KEY_REPLY = 232  # AC Reply
    KEY_FORWARDMAIL = 233  # AC Forward Msg
    KEY_SAVE = 234  # AC Save
    KEY_DOCUMENTS = 235

    KEY_BATTERY = 236

    KEY_BLUETOOTH = 237
    KEY_WLAN = 238
    KEY_UWB = 239

    KEY_UNKNOWN = 240

    KEY_VIDEO_NEXT = 241  # drive next video source
    KEY_VIDEO_PREV = 242  # drive previous video source
    KEY_BRIGHTNESS_CYCLE = 243  # brightness up, after max is min
    KEY_BRIGHTNESS_ZERO = 244  # brightness off, use ambient
    KEY_DISPLAY_OFF = 245  # display device to off state

    KEY_WIMAX = 246
    
class KeyEvent(enum.Enum):
    KEY_UP   = 0
    KEY_DOWN = 1
    KEY_HOLD = 2

class struct_timeval(ctypes.LittleEndianStructure):
    _fields_ = [
        ("tv_sec",  ctypes.c_long),
        ("tv_usec", ctypes.c_long),
    ]
               
class struct_input_event(ctypes.LittleEndianStructure):
    _fields_ = [
        ("time",  struct_timeval),
        ("type",  ctypes.c_ushort),
        ("code",  ctypes.c_ushort),
        ("value", ctypes.c_uint),
    ]

    def __str__(self) -> str:
        return f"InputEvent(type = {EventType(self.type)}, code = {self.code}, value = {self.value})"
