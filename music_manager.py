import random
import os
import sys
from collections import deque

from player import Player
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

        if not os.path.isdir("./music"):
            os.mkdir("./music")
        self.queue_size = queue_size
        self.not_recently_played = [x for x in list_dir("./music") if x.split(".")[-1].lower() in self.extensions]
        self.recently_played = deque()
        self.imminent_queue = deque()
        if sys.platform.startswith("win"):
            self.k = WindowKeyListener()
        if sys.platform.startswith("linux") or sys.platform.startswith("darwin"):
            self.k = UnixKeyListener()

    def fill_queue(self):
        while len(self.recently_played) > self.queue_size and len(self.recently_played) > 0:
            self.not_recently_played.append(self.recently_played.popleft())
        while len(self.imminent_queue) < self.queue_size and len(self.not_recently_played) > 0:
            self.imminent_queue.append(random.choice(self.not_recently_played))

    def next_music(self):
        current_music = self.imminent_queue.popleft()
        self.recently_played.append(current_music)
        self.fill_queue()
        return current_music


if __name__ == "__main__":
    mm = MusicManager()
    mm.fill_queue()
    while True:
        player = Player()
        state = player.play_ffplay(mm.next_music())
        if not state:
            break