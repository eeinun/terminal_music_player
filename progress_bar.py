import time


class ProgressBar:
    bar_comp = ([chr(x) for x in range(0x2589, 0x2590)] + [''])[::-1]
    def __init__(self, total=0.0, n=0.0, left="L", right="R"):
        self.total = total
        self.n = n
        self.left = left
        self.right = right
        self.bar = ""
        self.bar_edge = ""
        self.last_update = time.time() - 1

    def update(self, n):
        self.n = n
        if self.last_update + 0.01 < time.time():
            self.last_update = time.time()
            self.disp()

    def disp(self):
        # get terminal width
        import shutil
        self.bar = self.get_bar(shutil.get_terminal_size().columns - len(self.left) - len(self.right) - 2)
        print(f'\r{self.left}{chr(0x2595)}{self.bar}{chr(0x258f)}{self.right}', end='')

    def get_bar(self, w):
        if self.total == 0:
            return ""
        else:
            p = min(1.0, self.n / self.total)
            bei = int(p * w * 8) % 8
            self.bar_edge = self.bar_comp[bei]
            bar = chr(0x2588) * int(p * w) + self.bar_edge
            return bar + " " * (w - len(bar))

if __name__ == "__main__":
    pb = ProgressBar()
    pb.total = 100000000
    pb.disp()
    for i in range(100000000):
        pb.update(i)