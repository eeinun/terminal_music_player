import sys
from enum import Enum

class WindowKey(Enum):
    SPACE = b" "
    Q = b"q"
    ESCAPE = b"\xe0"
    RIGHT = b"\xe0M"
    LEFT = b"\xe0K"

class UnixKey(Enum):
    SPACE = " "
    Q = "q"
    ESCAPE = b"\x1b"
    RIGHT = b"\x1b[C"
    LEFT = b"\x1b[D"


class KeyListener:
    def __init__(self):
        self.keys = None
        self.event_action_table = dict()

    def add_event(self, key, action):
        self.event_action_table[key] = action

    def _detect(self):
        pass

    def handle(self):
        key = self._detect()
        if key in self.event_action_table:
            self.event_action_table[key]()

    def mirror(self):
        return self._detect()

class WindowKeyListener(KeyListener):
    import msvcrt
    def __init__(self):
        super().__init__()
        self.keys = WindowKey

    def _detect(self):
        if msvcrt.kbhit():
            k = msvcrt.getch()
            if k == self.keys.ESCAPE.value:
                k += msvcrt.getch()
            return k
        else:
            return None

class UnixKeyListener(KeyListener):
    import select
    def __init__(self):
        super().__init__()
        self.keys = UnixKey

    def _detect(self):
        if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
            k = sys.stdin.read(1)
            if k == self.keys.ESCAPE.value:
                k += sys.stdin.read(2)
                return k
            return None
        else:
            return None