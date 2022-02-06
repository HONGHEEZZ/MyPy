import os.path, time
#from datetime import datetime  # error in line: ref_date = ...
from datetime import datetime  # this works for me
import pytz
from win32com.propsys import propsys, pscon

GPS_NO_OPLOCK = 0x00000080  # not defined in propsys
# see https://docs.microsoft.com/en-us/windows/win32/api/propsys/ne-propsys-getpropertystoreflags
# see https://www.pinvoke.net/default.aspx/Enums.GETPROPERTYSTOREFLAGS
# see http://timgolden.me.uk/pywin32-docs/propsys__SHGetPropertyStoreFromParsingName_meth.html


def getFormatTimeStamp( fTimeStamp, fmt):

    dt = datetime.fromtimestamp(fTimeStamp)

    strDt = dt.strftime(fmt)

    return strDt

if __name__ == '__main__':

    folder = "E:\\Video\\2019"

    filename = "IMG_0267.MOV'"
    fullpath = r"E:\04.사진_원본\20210801_강영란_핸드폰\video\kakaotalk_1601552529989.mp4"
    print(f'filename {filename}  fullpath {fullpath}')

    # see https://stackoverflow.com/questions/61713787/reading-and-writing-windows-tags-with-python-3
    properties = propsys.SHGetPropertyStoreFromParsingName(fullpath, None, GPS_NO_OPLOCK,
                                                           propsys.IID_IPropertyStore)

    dt = properties.GetValue(pscon.PKEY_Media_DateEncoded).GetValue()
    if dt:
        KST = pytz.timezone('Asia/Seoul')
        new_dt = dt.astimezone(KST)
        print(new_dt.astimezone().strftime('%Y-%m-%d %H:%M:%S'))
    else:
        ts = os.path.getmtime(fullpath)  # 1507245810.6208477
        dt = datetime.fromtimestamp(ts)

        strDt = dt.strftime("%Y-%m-%d %H:%M:%S")

    zzz=9