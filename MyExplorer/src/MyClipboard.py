
import ctypes
from ctypes import wintypes
import pythoncom
import win32clipboard as cb32
import clipboard


#------------------------------------------------------------------------------
#* 클립보드 용 구조체
#------------------------------------------------------------------------------
class DROPFILES(ctypes.Structure):
    _fields_ = (('pFiles', wintypes.DWORD),
                ('pt',     wintypes.POINT),
                ('fNC',    wintypes.BOOL),
                ('fWide',  wintypes.BOOL))

class CMyClipboard():
    def __init__(self):
        pass

    #------------------------------------------------------------------------------
    #* 클립보드에 파일 리스트 쓰기
    #------------------------------------------------------------------------------
    def set_clip_files(self, file_list):
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
        cb32.OpenClipboard()
        try:
            cb32.SetClipboardData(cb32.CF_HDROP,
                                            stg.data)
        finally:
            cb32.CloseClipboard()

    # ------------------------------------------------------------------------------
    # * 클립보드에서 파일리스트를 가져온다.
    # ------------------------------------------------------------------------------
    def get_clip_files(self):
        cb32.OpenClipboard()

        flist = []
        if cb32.IsClipboardFormatAvailable(cb32.CF_HDROP):
            filenames = cb32.GetClipboardData(cb32.CF_HDROP)
            # for filename in filenames:
            #     flist.append(filename)

        cb32.CloseClipboard()

        return filenames


    def set_clip_strings(self, strList):

        full_str = ''
        for str in strList:
            full_str += str + '\n'

        clipboard.copy(full_str)

        return full_str