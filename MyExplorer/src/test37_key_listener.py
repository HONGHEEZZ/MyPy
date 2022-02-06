from pynput.keyboard import Listener, Key, KeyCode
import win32api

store = set()

HOT_KEYS = {
    'print_hello': set([Key.alt_l, KeyCode(char='1')])
    , 'open_notepad': set([Key.alt_l, KeyCode(char='2')])
}


def print_hello():
    print('hello, World!!!')


def open_notepad():
    print('open_notepad')
    try:
        win32api.WinExec('notepad.exe')
    except Exception as err:
        print(err)


def handleKeyPress(key, **kwargs):
    store.add(key)


def handleKeyRelease(key):
    for action, trigger in HOT_KEYS.items():
        CHECK = all([True if triggerKey in store else False for triggerKey in trigger])

        if CHECK:
            try:
                action = eval(action)
                if callable(action):
                    action()
            except NameError as err:
                print(err)

    # 종료
    if key == Key.esc:
        return False
    elif key in store:
        store.remove(key)


with Listener(on_press=handleKeyPress, on_release=handleKeyRelease) as listener:
    listener.join()