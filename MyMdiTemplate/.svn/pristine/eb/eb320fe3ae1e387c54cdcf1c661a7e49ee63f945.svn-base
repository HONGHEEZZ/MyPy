from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import main

import sys
#* 참고 필요
#https://programtalk.com/python-examples/PyQt5.Qt.QImage/


# img clibboard 저장용
from PyQt5.Qt import QApplication, QClipboard
from PyQt5.Qt import QImage

from PyQt5.QtGui import QPainter, QColor


#------------------------------------------------------------------------------
#* 신규버전 시작
#------------------------------------------------------------------------------
from io import BytesIO
import win32clipboard
from PIL import Image

def send_to_clipboard(clip_type, data):
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(clip_type, data)
    win32clipboard.CloseClipboard()

def img_to_clipboard(full_fname):
    #filepath = 'd:/imgs/class_cookie.png'
    filepath = full_fname
    image = Image.open(filepath)

    output = BytesIO()
    image.convert("RGB").save(output, "BMP")
    data = output.getvalue()[14:]
    output.close()

    send_to_clipboard(win32clipboard.CF_DIB, data)

#------------------------------------------------------------------------------
#* 신규버전 끝 
#------------------------------------------------------------------------------













def check_img_transparency(img):
    fmt = img.format()
    image = QImage(img)
    if (image.depth() == 1 and img.colorTable().size() == 2 and
            img.colorTable().at(0) == QColor(Qt.black).rgba() and
            img.colorTable().at(1) == QColor(Qt.white).rgba()):
        if fmt == QImage.Format_MonoLSB:
            image = image.convertToFormat(QImage.Format_Mono)
        fmt = QImage.Format_Mono
    else:
        if (fmt != QImage.Format_RGB32 and fmt != QImage.Format_ARGB32):
            image = image.convertToFormat(QImage.Format_ARGB32)
            fmt = QImage.Format_ARGB32

    w = image.width()
    h = image.height()
    d = image.depth()

    if fmt == QImage.Format_Mono:
        bytes_per_line = (w + 7) >> 3
        data = image.constBits().asstring(bytes_per_line * h)
        #return self.write_image(data, w, h, d, cache_key=cache_key)

    has_alpha = False
    soft_mask = None

    if fmt == QImage.Format_ARGB32:
        if image.hasAlphaChannel():
            # Blend image onto a white background as otherwise Qt will render
            # transparent pixels as black
            background = QImage(image.size(), QImage.Format_ARGB32_Premultiplied)
            background.fill(Qt.white)
            painter = QPainter(background)
            painter.drawImage(0, 0, image)
            painter.end()
            image = background
    return image

def send_img_to_clipboard(full_fname = "d:/imgs/class_cookie.png"):
    my_application = QApplication(sys.argv)

    f = open(full_fname, 'rb')

    img = QImage()
    img.loadFromData(f.read())

    f.close()

    img = check_img_transparency(img)

    data = QMimeData()
    data.setImageData(img)

    #clipboard = main.g_app.clipboard()

    clipboard = my_application.clipboard()
    clipboard.setMimeData(data)




if __name__=='__main__':
    import sys
    my_application = QApplication(sys.argv)
    send_img_to_clipboard("d:/imgs/class_cookie.png")
