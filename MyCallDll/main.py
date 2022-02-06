# This is a sample Python script.

# Press Ctrl+F5 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

# 파이썬에서 c언어의 함수를 사용하기 위해 ctypes 모듈 정의
from ctypes import *


def main():
    # !python
    # -*- coding: cp949 -*-
    # my_debugger.py




    Load_DLL = WinDLL('dll_test.dll')
    # 사용하고자할 모듈인 dll_test.dll 동적라이브러리 파일을 불러온다. ctypes.WinDLL('dll 파일 이름')
    plus_func = Load_DLL['plus']
    # Load_DLL에는 dll_test.dll 라이브러리에 대한 정보가 지녀졌으며 이 라이브러리에 포함된 함수인 plus 함수를 plus_func
    # 에 인스턴스로 저장한다.
    plus_func.argtypes = (c_int, c_int)
    # plus_func 함수의 인자 형식을 지정한다. plus 함수는 int 형 인자 2개를 받으므로 2개의 인자가 들어간다.
    plus_func.restype = c_int
    # plus_func 함수의 출력 형식을 지정한다.
    print('Arg PLUS')

    intA = int(input("arg1 : "))
    intB = int(input("arg2 : "))
    plus_res = plus_func(intA, intB)
    # 함수를 호출한 뒤 반환 값을 plus_res에 저장한다.
    print("Arg1 + Arg2 :", intA + intB, '\n')

    minus_func = Load_DLL['minus']
    minus_func.argtypes = (c_int, c_int, c_int)
    minus_func.restype = c_bool
    print('Arg MINUS')
    intA = int(input("arg1 : "))
    intB = int(input("arg2 : "))
    minus_res = minus_func(intA, intB, 0)

    if minus_res == True:
        print("Arg1 > Arg2")
        print("Arg1-Arg2 :", intA - intB)
    else:
        print("Arg1 <= Arg2")
        print("Arg1-Arg2 :", intA - intB)

    CDLL('dll_test.dll')
    # 호출된 dll_test.dll 연결을 종료한다.

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
