
import os
import sys
from ctypes import *
from ctypes.wintypes import MSG
from ctypes.wintypes import DWORD
import pyperclip # 클립보드
import copy #deep copy

import sys
sys.path.append('../MyLib')
from MyLog import logger
import win32api

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

class MyKeyHook:
    pointer = None

    @staticmethod
    def setHotkeys(hotkeys):
        MyKeyHook.myHotkeys = copy.deepcopy(hotkeys)

    @staticmethod
    def init():
        kernel32 = windll.kernel32
        MyKeyHook.hooked = None

    @staticmethod
    def start():
        MyKeyHook.init()
        MyKeyHook.pointer = MyKeyHook.getFPTR(MyKeyHook.hookProc)
        MyKeyHook.store = set()

        if MyKeyHook.installHookProc():
            logger.debug("install success...")
            MyKeyHook.listen()
        else:
            logger.debug("install failed.")

    @staticmethod
    def stop():
        if MyKeyHook.hooked:
            MyKeyHook.uninstallHookProc()
            logger.debug("uninstall hook...")
        else:
            logger.debug("already uninstalled.")

    @staticmethod
    def installHookProc():
        MyKeyHook.hooked = user32.SetWindowsHookExA(
            WM_KEYBOARD_LL,
            MyKeyHook.pointer,
            None,
            0
        )
        if MyKeyHook.hooked:
            logger.debug("hooked...")
            return True
        else:
            logger.debug('not hooked...')
        return False

    @staticmethod
    def hookProc(nCode, wParam, lParam):
        # logger.debug("I'm hookProc....")
        if wParam == WM_KEYDOWN:
            MyKeyHook.onKeyDown(nCode, wParam, lParam)
        elif wParam == WM_KEYUP:
            MyKeyHook.onkeyUp(nCode, wParam, lParam)
        return user32.CallNextHookEx(MyKeyHook.hooked, nCode, wParam, lParam)

    @staticmethod
    def getFPTR(fn):
        CMPFUNC = CFUNCTYPE(c_int, c_int, c_int, POINTER(c_void_p))
        return CMPFUNC(fn)

    @staticmethod
    def onKeyDown(nCode, wParam, lParam):
        keyCode = MyKeyHook.getKeyCode(lParam)
        # logger.debug(f"nCode:[{nCode}], wParam:[{wParam}], IParam:[{lParam}], ")
        hookedKey = chr(keyCode)
        MyKeyHook.store.add(keyCode)
        # logger.debug(store)

        if len(MyKeyHook.store) == 3:
            zz = 9

        # [strSeq, strTitle, strScDiv, strdoAction, keyUnion]
        for list in MyKeyHook.myHotkeys:
            strSeq = list[0]
            strTitle = list[1]
            strScDiv = list[2]
            strdoAction = list[3]
            keyUnion = list[4]

            CHECK = all([True if triggerKey in MyKeyHook.store else False for triggerKey in keyUnion])
            if CHECK:
                logger.debug('* ' + strTitle)
                MyKeyHook.doAction(list)

    @staticmethod
    def doAction(list):
        strSeq = list[0]
        strTitle = list[1]
        strScDiv = list[2]
        strdoAction = list[3]
        keyUnion = list[4]

        if strScDiv == "1. Run Program":
            #myCur = CMyCursor()
            win32api.ShellExecute(0, 'open', strdoAction, None, None, 1)
        elif strScDiv == "2. Clipboard":
            pyperclip.copy(strdoAction)
        else:
            logger.debug(f'****[doAction() 지정된 타입이 없음 : [{strTitle}] [{strScDiv}]')

    @staticmethod
    def onkeyUp(nCode, wParam, lParam):

        # logger.debug(f"nCode:[{nCode)], wParam:[{wParam}], lParam:[{lParam}], ")
        keyCode = MyKeyHook.getKeyCode(lParam)
        MyKeyHook.store.remove(keyCode)

    @staticmethod
    def uninstallHookProc():
        if MyKeyHook.hooked is None:
            return
        user32.UnhookWindowsHookEx(MyKeyHook.hooked)
        MyKeyHook.hooked = None

    @staticmethod
    def bytes(integer):
        return divmod(integer, 0x10000)

    @staticmethod
    def getKeyCode(lParam):
        high, low = MyKeyHook.bytes(lParam[0])
        return low

    @staticmethod
    def listen():
        msg = MSG()
        user32.GetMessageA(byref(msg), 0, 0, 0)

class MyFunc:
    @staticmethod
    def print_hello():
        logger.debug(" ***hello ***")

    @staticmethod
    def copy_pwd_to_clipboard():
        logger.debug("*** copy_pwd_to_clipboard ***")

        pyperclip.copy("icis0624!!")

    @staticmethod
    def uninstallHook():
        logger.debug("*** uninstall Hook ***")
        MyKeyHook.uninstallHookProc()
        os._exit(1)

if __name__ == "__main__":
    MyKeyHook = MyKeyHook()
    MyKeyHook.myInit()
    MyKeyHook.myKeyHookStart()
