from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic
import os
import win32com.client
import time
import re


my_dlg = uic.loadUiType("./ui/MyRe.ui")[0]


class CMyRe(QDialog, my_dlg):
    def __init__(self, parent=None):
        print("parent:", parent)
        super().__init__(parent)
        self.setupUi(self)
        # loadUi("test2",self)

        self.initUI()

        self.btnView.clicked.connect(self.btnView_Click)
        self.btnDoWork.clicked.connect(self.btnDoWork_Click)

        self.txtExtend.setText(r"cfg")
        self.txtSourceDir.setText(r"D:\test")
        self.txtTargetDir.setText(r"D:\test\out")
        self.txtRe.setText(r'property "(.+)"')

    def initUI(self):
        self.setWindowTitle('DocumentFormatConverter')

        self.setMinimumSize(200, 200)

        self.tblFiles.setColumnCount(2)
        self.tblFiles.setHorizontalHeaderLabels(["FileName", "Directory"])

        self.tblFiles.setColumnWidth(0, 200)
        self.tblFiles.setColumnWidth(1, 400)

        self.progressBar.reset()

        # self.tblFiles.rowcount = 1

    def btnView_Click(self):
        myDir = self.txtSourceDir.text()
        myExtend = self.txtExtend.text()
        if not myExtend.startswith('.'):
            myExtend = '.' + myExtend

        findSubDir = self.chkSubDir.isChecked()
        list = []
        search(list, myDir, myExtend, findSubDir)
        print(list)

        self.tblFiles.setRowCount(len(list))

        for i, file in enumerate(list):
            self.tblFiles.setItem(i, 0, QTableWidgetItem(file[1]))
            self.tblFiles.setItem(i, 1, QTableWidgetItem(file[0]))

    def btnDoWork_Click(self):

        out_Dir = self.txtTargetDir.text()

        cnt = self.tblFiles.rowCount()

        # 상태 진행바
        self.progressBar.setRange(0, cnt)

        strRe = self.txtRe.text()
        print(strRe)

        row = 0
        while True:
            cell = self.tblFiles.item(row, 1)
            dir_name = cell.text()

            cell = self.tblFiles.item(row, 0)
            file_name = cell.text()

            doWork(dir_name, file_name, out_Dir, strRe)
            row = row + 1
            # 상태 진행바
            self.progressBar.setValue(row)

            if row >= cnt: break

def doWork(dir_name, file_name, out_dir, strRe):
    full_file_name = os.path.join(dir_name, file_name)
    f_in = open(full_file_name, 'r')  # , encoding='UTF8'

    out_file_name = os.path.join(out_dir, file_name)
    f_out = open(out_file_name, 'w')  # , encoding='UTF8'

    lines = f_in.readlines()

    p = re.compile(strRe)

    lines_out = []
    for line_no, contents in enumerate(lines):
        m = p.search(contents)
        if m:
            lines_out.append(m[1] + '\n')


    f_out.writelines(lines_out)
    f_out.close()
    f_in.close()


def search(list, dir_name, myExtend, findSubDir = True):
    file_names = os.listdir(dir_name)

    for file_name in file_names:
        full_filename = os.path.join(dir_name, file_name)
        # print(full_filename)
        if findSubDir and os.path.isdir(full_filename):
            search(list, full_filename, myExtend, findSubDir)

        else:
            ext = os.path.splitext(full_filename)[-1]
            if ext == myExtend:
                print('*************pdf 파일임...', full_filename)
                # pdfTohtml(dir_name, file_name)
                # wordTotxt(dir_name, file_name)
                list.append([dir_name, file_name])





if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    ex = CMyRe()
    ex.show()
    sys.exit(app.exec_())

