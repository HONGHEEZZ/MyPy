import curses
import os
def main(win):
    win.nodelay(True)
    key=""
    win.clear()
    win.addstr("Detected key:")
    while 1:
        try:
            key=win.getkey()
            win.clear()
            win.addstr("Detectedd key:")
            win.addstr(str(key))
            if key == os.linesep:
                break
        except Exception as e:
            # no input
            pass
curses.wrapper(main)
