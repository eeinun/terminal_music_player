import shutil
import time

from progress_bar import ProgressBar


def visual_slice(string, w):
    s = ""
    l = 0
    i = 0
    while len(s) < len(string) and i < len(string) and l < w:
        s += string[i]
        l += 1 if string[i].isascii() else 2
        i += 1
    return s


def visual_len(string):
    l = 0
    for i in string:
        l += 1 if i.isascii() else 2
    return l


def to_time_str(seconds):
    m, s = divmod(seconds, 60)
    return f"{int(m):02d}:{s:05.2f}"


class PlayerTUI:
    def __init__(self, total, title = "", start=0.0):
        self.color = "\033[92m"
        self.pbar = ProgressBar(total=total, right=to_time_str(total), left=to_time_str(start))
        self.width = shutil.get_terminal_size().columns
        self.state_change = False
        self.title = "no title"
        print(self.color, end='')

    def set_title(self, title):
        self.title = title
        self.state_change = True

    def set_total(self, total):
        self.pbar.total = total
        self.pbar.right = to_time_str(total)
        self.state_change = True

    def proc_center(self, string):
        self.width = shutil.get_terminal_size().columns
        if visual_len(string) > self.width:
            title = visual_slice(string, self.width - 5) + "..."
        else:
            title = string
        vl = visual_len(title)
        pad = (self.width - vl) // 2
        return ' ' * pad + title + ' ' * (self.width - vl - pad)

    def clear_frame(self):
        print("\033[H\033[K\033[2J\033[3J\033[?25l" + self.color, end='')

    def update_frame(self, n: float):
        if self.width != shutil.get_terminal_size().columns or self.state_change:
            self.state_change = False
            self.width = shutil.get_terminal_size().columns
            self.clear_frame()
            print(self.proc_center(self.title))
            print()
        self.pbar.n = n
        self.pbar.left = to_time_str(n)
        self.pbar.disp()


if __name__ == "__main__":
    pt = PlayerTUI(10, title = "Test")
    for i in range(1001):
        pt.update_frame(i / 100)
        time.sleep(0.02)
    print("\033[38;2;255;255;255m")
