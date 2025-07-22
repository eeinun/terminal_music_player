import subprocess
import os
import re
import sys
import time
import shutil
import argparse
import psutil

from player_tui import PlayerTUI
from key_listener import WindowKeyListener, UnixKeyListener


def proc_str(string) -> tuple[int, float]:
    if string.startswith("Duration"):
        h, m, s, ms = map(int, (re.findall(r'Duration: (\d\d):(\d\d):(\d\d).(\d\d).+', string) + [(0, 0, -1, 0)])[0])
        return 0, h * 3600 + m * 60 + s + ms / 1000
    m = re.match(r'(-?\d+\.\d+)\s*[\w\-]+:\s*\d+\.\d+(\s*\w+=\s*\d+\w*)*', string)
    if m is not None:
        return 1, float(m.group(1))
    else:
        return -1, 0.0


def to_time_str(seconds):
    m, s = divmod(seconds, 60)
    return f"{int(m):02d}:{s:05.2f}"


def proc_center(string):
        w = shutil.get_terminal_size().columns
        if visual_len(string) > w:
            title = visual_slice(string, w - 7) + "..."
        else:
            title = string
        vl = visual_len(title)
        pad = (w - vl - 1) // 2
        return ' ' * pad + title + ' ' * (w - vl - pad)

def visual_len(string):
    l = 0
    for i in string:
        l += 1 if i.isascii() else 2
    return l

def visual_slice(string, w):
    s = ""
    l = 0
    while len(s) < len(string) and l < w:
        s += string[l]
        l += 1 if string[l].isascii() else 2
    return s

class Player:
    def __init__(self):
        self.proc = None
        self.k = WindowKeyListener() if sys.platform.startswith("win") else UnixKeyListener()
        self.p = None
        self.playing = True
        self.pt = PlayerTUI(1)
        self.framerate = 1 / 60
        self.t = time.time()
        self.current_music = None
        self.event_action_table = {
            self.k.keys.SPACE.value: self.pause_music,
            self.k.keys.Q.value: self.kill_music,
            self.k.keys.RIGHT.value: self.skip_music,
            self.k.keys.LEFT.value: self.replay
        }

    def get_command(self):
        return ['ffplay', '-nodisp', '-autoexit', '-af', 'volume=0.1', self.current_music]

    def dispatch_player(self):
        if self.proc is not None:
            self.proc.terminate()
        self.proc = subprocess.Popen(
            self.get_command(),
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )
        self.p = psutil.Process(self.proc.pid)

    def pause_music(self):
        if self.playing:
            self.playing = False
            self.p.suspend()
        else:
            self.playing = True
            self.p.resume()
        return True, True

    def kill_music(self):
        self.p.kill()
        return False, False

    def skip_music(self):
        self.p.kill()
        return False, True

    def replay(self):
        self.dispatch_player()
        return True, True

    def process_key_event(self):
        if kv := self.k.mirror():
            if kv in self.event_action_table:
                return self.event_action_table[kv]()
        return True, True

    def play_ffplay(self, file_path):
        self.current_music = file_path
        try:
            self.dispatch_player()
            audio_title = os.path.basename(file_path)
            self.pt.set_title(audio_title)
            self.t = time.time()
            while self.proc.poll() is None:
                # process key event
                e, w = self.process_key_event()
                if not e:
                    break
                if not w:
                    return False
                # consume one line
                if not self.playing:
                    continue
                line = self.proc.stderr.readline()
                if time.time() - self.t < self.framerate:
                    continue
                if not line:
                    time.sleep(self.framerate)
                    continue
                # update player ui
                t, v = proc_str(line.strip())
                if t == 0:
                    self.pt.set_total(v)
                elif t == 1:
                    self.pt.update_frame(v)
            self.proc.wait()
            self.proc = None
        except Exception as e:
            print(f"오류 발생: {e}")
            return False
        finally:
            if self.proc is not None:
                self.proc.terminate()
            print("\033[m\033[?25h", end="")
        return True


if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-f', '--file', type=str, required=True, help='file path')
    args = argparser.parse_args()
    player = Player()
    player.play_ffplay(args.file)
