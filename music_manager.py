import random
import os
import sys
import time
import argparse
from collections import deque

from player import Player
from constants.signals import PlaySignal

def list_dir(root_dir, extension_filter=None):
    """
    Traverse the directory recursively and return the file path list.
    :param root_dir: A path of the root directory
    :param extension_filter: A list of wanted extensions.
    :return:
    """
    ls = []
    for p in os.listdir(root_dir):
        if p == "cache":
            continue
        if os.path.isdir(f'{root_dir}/{p}'):
            ls += list_dir(f'{root_dir}/{p}')
        elif extension_filter is not None and p.split(".")[-1].lower() in extension_filter or extension_filter is None:
            ls.append(root_dir + "/" + p)
    return ls

def alert(msg):
    print()
    print(msg)
    sys.stdin.read(1)


class MusicManager:
    extensions = ["opus", "mp3", "flac", "wav"]

    @staticmethod
    def push_n_pop(q: deque, item, left=True):
        if len(q) == 0:
            return None
        if left:
            popped = q.pop()
            q.appendleft(item)
        else:
            popped = q.popleft()
            q.append(item)
        return popped

    def __init__(self, music_path=None, queue_size=5):
        self.current_music = None
        if music_path is None:
            music_path = "./music"
        if not os.path.isdir(music_path):
            os.mkdir(music_path)
        self.queue_size = queue_size
        self.music_path = music_path
        self.music_list = []
        self.recently_played = deque(maxlen=queue_size)
        self.imminent_queue = deque(maxlen=queue_size)
        self.backstack = []
        self.fill_queue()

    def fill_queue(self):
        # refresh music list
        self.music_list = [p for p in list_dir(self.music_path, self.extensions)]
        while len(self.imminent_queue) < self.queue_size and (len(self.music_list) - len(self.imminent_queue) - len(self.recently_played)) > 0:
            self.imminent_queue.append(self.get_new_music())

    def get_new_music(self):
        self.music_list = [p for p in list_dir(self.music_path, self.extensions)]
        nru = list(set(self.music_list) - set(self.recently_played + self.imminent_queue))
        if len(nru) == 0:
            return None
        return random.choice(nru)

    def next_music(self):
        if len(self.imminent_queue) == 0:
            self.fill_queue()
        if self.current_music is not None:
            self.backstack.append(self.current_music)
        self.current_music = self.push_n_pop(self.imminent_queue, self.get_new_music(), left=False)
        self.recently_played.append(self.current_music)
        return self.current_music

    def back_stack_pop(self):
        if len(self.backstack) == 0:
            return self.current_music
        self.push_n_pop(self.imminent_queue, self.current_music)
        self.current_music = self.backstack.pop()
        return self.current_music


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--volume', type=int, required=False, default=10, help='volume level')
    parser.add_argument('--key', action='store_true', required=False, help='display key bindings')
    parser.add_argument('--path', required=False, default=None, help='music folder path. default is "./music"')
    args = parser.parse_args()
    if args.key:
        print("Key bindings:")
        print("  Q: exit")
        print("  R: replay")
        print("  SPACE: pause/resume")
        print("  LEFT: back")
        print("  RIGHT: next")
        sys.exit(0)
    mm = MusicManager(music_path=args.path)
    Player.volume = args.volume / 100
    polling_count = 0
    max_polling_count = 300
    while len(list_dir(mm.music_path, mm.extensions)) == 0:
        polling_count += 1
        if polling_count >= max_polling_count:
            break
        print(f"\rNo music found. Waiting [{polling_count}/{max_polling_count}]", end='')
        time.sleep(1)
    current_music = mm.next_music()

    while True:
        player = Player()
        signal = player.play(current_music)
        time.sleep(0.2)
        if not signal:
            break
        if signal == PlaySignal.BACK:
            current_music = mm.back_stack_pop()
        elif signal == PlaySignal.EXIT:
            break
        else:
            current_music = mm.next_music()