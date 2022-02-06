import sys
from PyQt5.QtGui import QGuiApplication
from PyQt5.Qt import QApplication, QClipboard
from PyQt5 import QtWidgets

from PyQt5.QtCore import QMimeData

if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)

    clipboard = QGuiApplication.clipboard()
    clipboard.clear()

    data = QMimeData()
    #data.setText("hanhonghee 만세....")
    data.setHtml("<b>Bold and <font color=red>Red</font></b>")
    clipboard.setMimeData(data)

    clipboard = QGuiApplication.clipboard()
    mimeData = clipboard.mimeData()
    print(clipboard)
    for format in mimeData.formats():
        print(f'{format}: {mimeData.data(format)}')

