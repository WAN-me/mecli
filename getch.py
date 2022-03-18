import os
import sys
try:
    import sys, tty, termios
except ImportError:
    import msvcrt
class Getch:
    def __init__(self):
        if os.name == "posix":
            self.impl = _GetchUnix()
        else:
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
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class _GetchWindows:
    def __init__(self):
        import msvcrt
    def __call__(self):
        return msvcrt.getch().decode('cp866')

if __name__ == "__main__":
    handler = Getch()
    while True:
        key = handler()