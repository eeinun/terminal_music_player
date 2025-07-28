import sys
import os
if sys.platform.startswith("win"):
    import msvcrt
else:
    import select
    import tty
    import termios
    import atexit
from constants.keys import UnixKey, WindowKey


class KeyListener:
    def __init__(self):
        self.keys = None
        self.event_action_table = dict()
        self.key_buffer = b''

    def add_event(self, key, action):
        self.event_action_table[key] = action

    def _detect(self):
        pass

    def _process_control_sig(self, key_value):
        pass

    def handle(self):
        key = self._detect()
        if key is None:
            return True, True
        if key in self.event_action_table:
            return self.event_action_table[key]()
        return True, True

    def mirror(self):
        return self._detect()

class WindowKeyListener(KeyListener):
    def __init__(self):
        super().__init__()
        self.keys = WindowKey

    def _detect(self):
        k = b''
        while msvcrt.kbhit():
            k += msvcrt.getch()
        if len(k):
            return k
        else:
            return None


class UnixKeyListener(KeyListener):
    _original_terminal_settings = None

    def __init__(self):
        super().__init__()
        self.keys = UnixKey
        self._set_nonblocking_terminal()
        atexit.register(self._reset_terminal)

    def _set_nonblocking_terminal(self):
        if sys.stdin.isatty():
            UnixKeyListener._original_terminal_settings = termios.tcgetattr(sys.stdin)
            tty.setcbreak(sys.stdin.fileno())
        else:
            print("Warning: Standard input is not a TTY")

    def _reset_terminal(self):
        if sys.stdin.isatty() and UnixKeyListener._original_terminal_settings:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, UnixKeyListener._original_terminal_settings)

    def _detect(self):
        key = b''
        while sys.stdin.isatty() and select.select([sys.stdin], [], [], 0.001)[0]:
            cnt = len(select.select([sys.stdin], [], [], 0)[0][0].buffer.peek())
            key = sys.stdin.read(cnt).encode()
        if len(key):
            return key
        return None


if __name__ == "__main__":
    import time
    kl = None
    if sys.platform.startswith("win"):
        kl = WindowKeyListener()
        print("OS: Windows")
    elif sys.platform.startswith("linux") or sys.platform == "darwin":
        kl = UnixKeyListener()
        print("OS: Linux/macOS")
    else:
        print("OS: Unknown")
        sys.exit(1)
    env = sys.platform

    def on_space_press():
        print("[SPACE]")

    def on_right_press():
        print("[ARROW_RIGHT]")

    def on_left_press():
        print("[ARROW_LEFT]")

    def on_q_press():
        print("[Q]")

    def on_r_press():
        print("[R]")

    # 이벤트 등록
    if kl:
        kl.add_event(kl.keys.SPACE.value, on_space_press)
        kl.add_event(kl.keys.Q.value, on_q_press)
        kl.add_event(kl.keys.R.value, on_r_press)
        kl.add_event(kl.keys.RIGHT.value, on_right_press)
        kl.add_event(kl.keys.LEFT.value, on_left_press)

    print("Registered keys are")
    for k in kl.event_action_table:
        print('\t', end='')
        kl.event_action_table[k]()
    print()

    # 무한 루프에서 키 입력 감지
    try:
        while True:
            if kl:
                kl.handle() # 키 입력 처리
            # 다른 주기적인 작업을 여기에 추가할 수 있습니다.
            time.sleep(0.01) # CPU 과부하 방지
    except KeyboardInterrupt:
        print("\nkeyboard interrupt (Ctrl+C)")
    finally:
        print("\nProgram terminated.")