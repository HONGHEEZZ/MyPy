
import os
import sys
from ctypes import *
from ctypes.wintypes import MSG
from ctypes.wintypes import DWORD
import pyperclip # 클립보드

user32 = windll.user32
kernel32 = windll.kernel32

WM_KEYBOARD_LL = 13
WM_KEYDOWN = 256 # Ox0100
WM_KEYUP = 257 # 0x0101


CTRL_CODE = 162
SHFT_CODE = 160

store = set()
HOT_KEYS = {
    'MyFunc.print_hello': set([162, ord('5')]),
    'MyFunc.copy_pwd_to_clipboard': set([162, 160, ord('V')]),
    'MyFunc.uninstallHook': set([162, 160, ord('9')])
}

class KeyLog:
    pointer = None

    @staticmethod
    def myInit():
        kernel32 = windll.kernel32
        KeyLog.hooked = None

    @staticmethod
    def myKeyHookStart():
        KeyLog.pointer = KeyLog.getFPTR(KeyLog.hookProc)
        store = set()

        if KeyLog.installHookProc():
            print("install success...")
            KeyLog.listen()
        else:
            print("install failed.")

    @staticmethod
    def installHookProc():
        KeyLog.hooked = user32.SetWindowsHookExA(
            WM_KEYBOARD_LL,
            KeyLog.pointer,
            None,
            0
        )
        if KeyLog.hooked:
            print("hooked...")
            return True
        else:
            print('not hooked...')
        return False

    @staticmethod
    def hookProc(nCode, wParam, lParam):
        # print("I'm hookProc....")
        if wParam == WM_KEYDOWN:
            KeyLog.onKeyDown(nCode, wParam, lParam)
        elif wParam == WM_KEYUP:
            KeyLog.onkeyUp(nCode, wParam, lParam)
        return user32.CallNextHookEx(keylog.hooked, nCode, wParam, lParam)

    @staticmethod
    def getFPTR(fn):
        CMPFUNC = CFUNCTYPE(c_int, c_int, c_int, POINTER(c_void_p))
        return CMPFUNC(fn)

    @staticmethod
    def onKeyDown(nCode, wParam, lParam):
        keyCode = keylog.getKeyCode(lParam)
        # print(f"nCode:[{nCode)], wParam:[{wParam}], lParam:[{[Param}], ")
        hookedKey = chr(keyCode)
        store.add(keyCode)
        # print(store)
        for action, trigger in HOT_KEYS.items():
            CHECK = all([True if triggerkey in store else False for triggerkey in trigger])
            if CHECK:
                try:
                    func = eval(action)
                    if callable(func):
                        func()
                except NameError as err:
                    print(err)

    @staticmethod
    def onkeyUp(nCode, wParam, lParam):

        # print(f"nCode:[{nCode)], wParam:[{wParam}], lParam:[{lParam}], ")
        keyCode = keylog.getKeyCode(lParam)
        store.remove(keyCode)



    @staticmethod
    def uninstallHookProc():
        if KeyLog.hooked is None:
            return
        user32.UnhookWindowsHookEx(KeyLog.hooked)
        KeyLog.hooked = None

    @staticmethod
    def bytes(integer):
        return divmod(integer, 0x10000)

    @staticmethod
    def getKeyCode(lParam):
        high, low = KeyLog.bytes(lParam[0])
        return low

    @staticmethod
    def listen():
        msg = MSG()
        user32.GetMessageA(byref(msg), 0, 0, 0)

class MyFunc:
    @staticmethod
    def print_hello():
        print(" ***hello ***")

    @staticmethod
    def copy_pwd_to_clipboard():
        print("*** copy_pwd_to_clipboard ***")

        pyperclip.copy("icis0624!!")

    @staticmethod
    def uninstallHook():
        print("*** uninstall Hook ***")
        keylog.uninstallHookProc()
        os._exit(1)

if __name__ == "__main__":
    keylog = KeyLog()
    keylog.myInit()
    keylog.myKeyHookStart()
