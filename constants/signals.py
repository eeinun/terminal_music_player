from enum import Enum


class PlaySignal(Enum):
    EXIT = 0
    SKIP = 1
    BACK = 2
    CONTINUE = 3
    REPLAY = 4
