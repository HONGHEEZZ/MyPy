import sys

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic
import os
import time

from datetime import datetime

my_dlg = uic.loadUiType("ui/MyFileInfo.ui")[0]


class MyFileInfo(QDialog, my_dlg):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setupUi(self)

        self.id = None
        self.password = None

        self.m_checkBox = []

        self.setupUI()

    def setupUI(self):
        # self.setGeometry(1100, 200, 300, 100)
        # self.setWindowTitle("Sign In")
        # self.setWindowIcon(QIcon('icon.png'))

        self.btnChangeMtime.clicked.connect(self.btnChangeMtime_Click)
        pass


    def setUrl(self, fpath):
        self.txtUrl.setText(fpath)
        self.fpath = fpath

        mydir = fpath       # directory
        fname = ''          # 파일명
        
        if os.path.isfile(fpath):
            mydir, fname = os.path.split(fpath)

        self.txtDirName.setText(mydir)
        self.txtFileName.setText(fname)

        #1970년 1월 1일 0시로부터 현재까지 경과 초
        ts = os.path.getctime(fpath)    #1507245810.6208477  --> timestamp 하나의 숫자로 나타내는 시간
        file_dt = self.getFormatTimeStamp(ts, "%Y-%m-%d %H:%M:%S")
        self.txtChangeTime.setText(file_dt)

        ts = os.path.getmtime(fpath)  # 1507245810.6208477
        file_dt = self.getFormatTimeStamp(ts, "%Y-%m-%d %H:%M:%S")
        self.txtModifyTime.setText(file_dt)

        ts = os.path.getatime(fpath)  # 1507245810.6208477
        file_dt = self.getFormatTimeStamp(ts, "%Y-%m-%d %H:%M:%S")
        self.txtAccessTime.setText(file_dt)

    def getFormatTimeStamp(self, fTimeStamp, fmt):

        dt = datetime.fromtimestamp(fTimeStamp)

        strDt = dt.strftime(fmt)

        return strDt

    def btnChangeMtime_Click(self):
        #os.utime(fpath, (atime, mtime))함수를 이용하면 파일의 수정시간(mtime)과 접근시간(atime)을 변경할 수 있다.
        dt = self.txtModifyTime.text()
        ts = time.mktime(datetime.strptime(dt, '%Y-%m-%d %H:%M:%S').timetuple())

        fpath = self.txtUrl.text()

        os.utime(fpath, (ts, ts))

if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    dlg = MyFileInfo()
    dlg.exec_()
