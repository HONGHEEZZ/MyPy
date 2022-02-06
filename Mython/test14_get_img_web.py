from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

#* 참고 필요
#https://programtalk.com/python-examples/PyQt5.Qt.QImage/


# img clibboard 저장용
from PyQt5.Qt import QApplication, QClipboard
from PyQt5.Qt import QImage

from PyQt5.QtGui import QPainter, QColor


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

def send_to_clipboard():
    my_application = QApplication(sys.argv)

    f = open("d:/imgs/class_cookie.png", 'rb')

    img = QImage()
    img.loadFromData(f.read())

    f.close()

    img = check_img_transparency(img)

    data = QMimeData()
    data.setImageData(img)

    clipboard = my_application.clipboard()
    clipboard.setMimeData(data)



if __name__=='__main__':
    import sys
    my_application = QApplication(sys.argv)
    send_to_clipboard()
