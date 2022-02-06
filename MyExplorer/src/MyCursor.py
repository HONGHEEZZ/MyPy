from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class CMyCursor():
    def __init__(self, cursorType=Qt.WaitCursor):
        # QApplication.setOverrideCursor(Qt.WaitCursor)
        QApplication.setOverrideCursor(cursorType)

    # * 소멸자
    def __del__(self):
        QApplication.restoreOverrideCursor()
