import random
import os
import sys
import argparse
from collections import deque

from player import Player
from constants.signals import PlaySignal
from key_listener import WindowKeyListener, UnixKeyListener

def list_dir(root_dir):
    ls = []
    for p in os.listdir(root_dir):
        if os.path.isdir(f'{root_dir}/{p}'):
            ls += list_dir(f'{root_dir}/{p}')
        else:
            ls.append(root_dir + "/" + p)
    return ls


class MusicManager:
    music_list_path = "./music.txt"
    extensions = ["opus", "mp3", "flac", "wav"]
    def __init__(self, queue_size=5):
        self.current_music = None
        if not os.path.isdir("./music"):
            os.mkdir("./music")
        self.queue_size = queue_size
        self.not_recently_played = [x for x in list_dir("./music") if x.split(".")[-1].lower() in self.extensions]
        self.recently_played = deque()
        self.imminent_queue = deque()
        self.backstack = []
        if sys.platform.startswith("win"):
            self.k = WindowKeyListener()
        if sys.platform.startswith("linux") or sys.platform.startswith("darwin"):
            self.k = UnixKeyListener()

    def fill_queue(self):
        while len(self.recently_played) > self.queue_size and len(self.recently_played) > 0:
            self.not_recently_played.append(self.recently_played.popleft())
        while len(self.imminent_queue) < self.queue_size and len(self.not_recently_played) > 0:
            self.imminent_queue.append(random.choice(self.not_recently_played))

    def next_music(self, back=False):
        if back and len(self.backstack) > 0:
            return self.backstack.pop()
        if len(self.imminent_queue) == 0:
            self.fill_queue()
        self.current_music = self.imminent_queue.popleft()
        self.recently_played.append(self.current_music)
        self.fill_queue()
        return self.current_music

    def back_stack_pop(self):
        if len(self.backstack) == 0:
            return self.current_music
        self.imminent_queue.appendleft(self.current_music)
        self.current_music = self.backstack.pop()
        return self.current_music


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--volume', type=int, required=False, default=10, help='volume level')
    parser.add_argument('--key', action='store_true', required=False, help='display key bindings')
    args = parser.parse_args()
    if args.key:
        print("Key bindings:")
        print("  Q: exit")
        print("  R: replay")
        print("  SPACE: pause/resume")
        print("  LEFT: back")
        print("  RIGHT: next")
        sys.exit(0)
    mm = MusicManager()
    mm.fill_queue()
    Player.volume = args.volume / 100
    current_music = mm.next_music()
    while True:
        player = Player()
        state = player.play(current_music)
        if not state:
            break
        if state == PlaySignal.BACK:
            current_music = mm.back_stack_pop()
        elif state == PlaySignal.EXIT:
            break
        else:
            mm.backstack.append(current_music)
            current_music = mm.next_music()