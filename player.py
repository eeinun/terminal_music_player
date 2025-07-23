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
from constants.signals import PlaySignal


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
    volume = 0.1
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
            self.k.keys.LEFT.value: self.back,
            self.k.keys.R.value: self.replay
        }
        self.k.event_action_table = self.event_action_table

    def get_command(self):
        return ['ffplay', '-nodisp', '-autoexit', '-af', f'volume={self.volume}', self.current_music]

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

    # action functions. PlaySignal
    def pause_music(self) -> PlaySignal:
        if self.playing:
            self.playing = False
            self.p.suspend()
        else:
            self.playing = True
            self.p.resume()
        return PlaySignal.CONTINUE

    def kill_music(self) -> PlaySignal:
        self.p.kill()
        return PlaySignal.EXIT

    def skip_music(self) -> PlaySignal:
        self.p.kill()
        return PlaySignal.SKIP

    def back(self) -> PlaySignal:
        self.p.kill()
        return PlaySignal.BACK

    def replay(self) -> PlaySignal:
        self.dispatch_player()
        return PlaySignal.REPLAY

    # main play loop
    def play(self, file_path):
        self.current_music = file_path
        try:
            self.dispatch_player()
            audio_title = os.path.basename(file_path)
            self.pt.set_title(audio_title)
            self.t = time.time()
            while self.proc.poll() is None:
                # process key event
                psig = self.k.handle()
                # control flow
                if psig == PlaySignal.EXIT:
                    return PlaySignal.EXIT
                if psig == PlaySignal.BACK:
                    return PlaySignal.BACK
                if psig == PlaySignal.SKIP:
                    break
                if psig == PlaySignal.REPLAY:
                    continue
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
            return PlaySignal.EXIT
        finally:
            if self.proc is not None:
                self.proc.terminate()
            print("\033[m\033[?25h", end="")
        return PlaySignal.SKIP


if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-f', '--file', type=str, required=True, help='file path')
    args = argparser.parse_args()
    player = Player()
    player.play(args.file)
