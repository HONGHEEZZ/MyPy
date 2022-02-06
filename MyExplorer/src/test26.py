import ctypes
from ctypes import wintypes
import pythoncom
import win32clipboard

#------------------------------------------------------------------------------
#* 클립보드 용 구조체
#------------------------------------------------------------------------------
class DROPFILES(ctypes.Structure):
    _fields_ = (('pFiles', wintypes.DWORD),
                ('pt',     wintypes.POINT),
                ('fNC',    wintypes.BOOL),
                ('fWide',  wintypes.BOOL))

#------------------------------------------------------------------------------
#* 클립보드에 파일 리스트 쓰기
#------------------------------------------------------------------------------
def set_clip_files(file_list):
    offset = ctypes.sizeof(DROPFILES)
    length = sum(len(p) + 1 for p in file_list) + 1
    size = offset + length * ctypes.sizeof(ctypes.c_wchar)
    buf = (ctypes.c_char * size)()
    df = DROPFILES.from_buffer(buf)
    df.pFiles, df.fWide = offset, True
    for path in file_list:
        array_t = ctypes.c_wchar * (len(path) + 1)
        path_buf = array_t.from_buffer(buf, offset)
        path_buf.value = path
        offset += ctypes.sizeof(path_buf)
    stg = pythoncom.STGMEDIUM()    
    stg.set(pythoncom.TYMED_HGLOBAL, buf)
    win32clipboard.OpenClipboard()
    try:
        win32clipboard.SetClipboardData(win32clipboard.CF_HDROP,
                                        stg.data)
    finally:
        win32clipboard.CloseClipboard()

#------------------------------------------------------------------------------
#* 클립보드 파일 리스트 읽기
#------------------------------------------------------------------------------
def get_clip_files():
    import win32clipboard as cb

    cb.OpenClipboard()

    if cb.IsClipboardFormatAvailable(cb.CF_HDROP):
        filenames = cb.GetClipboardData(cb.CF_HDROP)
        for filename in filenames:
            print(filename)

    cb.CloseClipboard()


if __name__ == '__main__':
    #import os
    #clip_files([os.path.abspath(__file__)])

    import os

    root_dir = 'D:/test3'
    item_list = os.listdir(root_dir)
    set_clip_files(['d:/test3/text01.txt', 'd:/test3/text02.txt', 'd:/test3/text03.txt' ])

    get_clip_files()
