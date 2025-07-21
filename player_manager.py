import psutil
import sys
from player import Player
from key_listener import WindowKeyListener, UnixKeyListener


"""
control ffplay master class 
- create player instance
- get PID of ffplay process
- kill/suspend/resume process by given key
"""


class PlayerManager:
    def __init__(self):
        self.player = Player()
        self.ffplay_pid = None
        if sys.platform.startswith("win"):
            self.k = WindowKeyListener()
        elif sys.platform.startswith("linux") or sys.platform.startswith("darwin"):
            self.k = UnixKeyListener()
        else:
            raise Exception("Unknown platform. Only supports Windows and Linux. Mac can be supported but never have been tested.")

    def play(self, path):
        self.player.play_ffplay(path)