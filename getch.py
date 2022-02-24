import os
import sys, tty, termios
try:
    import sys, tty, termios
except ImportError:
    import msvcrt
class Getch:
    def __init__(self):
        try:
            self.impl = _GetchUnix()
        except ImportError:
            self.impl = _GetchWindows()

    def __call__(self): 
        return self.impl()


class _GetchUnix:
    def __init__(self):
        import tty, termios
        os.system('stty -ixon')
    def __call__(self):
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setcbreak(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class _GetchWindows:
    def __init__(self):
        import msvcrt
    def __call__(self):
        return msvcrt.getch()

if __name__ == "__main__":
    handler = Getch()
    while True:
        key = handler()