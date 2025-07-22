import sys
import select
import tty
import termios
import time
import atexit


def reset(original_terminal_settings):
    def _reset_terminal():
        if sys.stdin.isatty() and original_terminal_settings:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, original_terminal_settings)
    return _reset_terminal

if sys.stdin.isatty():
    original_terminal_settings = termios.tcgetattr(sys.stdin)
    tty.setcbreak(sys.stdin.fileno())
else:
    print("Warning: Standard input is not a TTY")


atexit.register(reset(original_terminal_settings))

for i in range(100000):
    key = b''
    while sys.stdin.isatty() and select.select([sys.stdin], [], [], 0.001)[0]:
        cnt = len(select.select([sys.stdin], [], [], 0)[0][0].buffer.peek())
        key = sys.stdin.read(cnt).encode()
    if len(key):
        print(str(key))