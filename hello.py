import sys
import os

if os.name == 'nt':
    import msvcrt
else:
    import curses

class MenuSelector:
    def __init__(self, options):
        self.options = options
        self.index = 0

    def run(self):
        if os.name == 'nt':
            self.run_windows()
        else:
            curses.wrapper(self.run_unix)

    # Windows用（msvcrt）
    def run_windows(self):
        while True:
            os.system('cls')
            for i, opt in enumerate(self.options):
                prefix = "→" if i == self.index else "  "
                print(f"{prefix} {opt}")

            key = msvcrt.getch()
            if key == b'\xe0':  # 矢印キーの前置コード
                direction = msvcrt.getch()
                if direction == b'H':  # ↑
                    self.index = (self.index - 1) % len(self.options)
                elif direction == b'P':  # ↓
                    self.index = (self.index + 1) % len(self.options)
            elif key == b'\r':  # Enter
                print(f"\n選ばれたのは: {self.options[self.index]}")
                break

    # Mac/Linux用（curses）
    def run_unix(self, stdscr):
        curses.curs_set(0)
        stdscr.nodelay(False)
        stdscr.keypad(True)

        while True:
            stdscr.clear()
            for i, opt in enumerate(self.options):
                prefix = "→" if i == self.index else "  "
                stdscr.addstr(f"{prefix} {opt}\n")

            key = stdscr.getch()
            if key == curses.KEY_UP:
                self.index = (self.index - 1) % len(self.options)
            elif key == curses.KEY_DOWN:
                self.index = (self.index + 1) % len(self.options)
            elif key in [curses.KEY_ENTER, 10, 13]:
                stdscr.addstr(f"\n選ばれたのは: {self.options[self.index]}")
                stdscr.refresh()
                stdscr.getch()
                break

if __name__ == "__main__":
    options = ["Option 1", "Option 2", "Option 3", "Option 4"]
    selector = MenuSelector(options)
    selector.run()