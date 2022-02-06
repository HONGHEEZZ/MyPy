from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic
import os
import win32com.client
import time

import re
import cx_Oracle

word = win32com.client.Dispatch("Word.Application")

my_dlg = uic.loadUiType("./ui/FileUploader.ui")[0]


class CFileUploader(QDialog, my_dlg):
    def __init__(self, parent=None):
        print("parent:", parent)
        super().__init__(parent)
        self.setupUi(self)
        # loadUi("test2",self)

        self.initUI()

        self.btnView.clicked.connect(self.btnView_Click)
        self.btnUpload.clicked.connect(self.btnUpload_Click)

        self.txtExtend.setText("cfg")
        self.txtSourceDir.setText(r"D:\test\output")
        self.txtConnStr.setText(r"han/han@192.168.0.10:1521/orcl")

        self.txtTableName.setText(r"RW_FILES_GENERAL")
        self.txtDeleteSql.setText(r"etc1 = 'keyword'")


        self.txtEtc1.setText(r"keyword")


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
        myExtend = myExtend.strip()

        if myExtend != '':
            if not myExtend.startswith('.'):
                myExtend = '.' + myExtend

        list = []


        search(list, myDir, myExtend)
        print(list)

        self.tblFiles.setRowCount(len(list))

        for i, file in enumerate(list):
            self.tblFiles.setItem(i, 0, QTableWidgetItem(file[1]))
            self.tblFiles.setItem(i, 1, QTableWidgetItem(file[0]))

    def btnUpload_Click(self):

        conn_str = self.txtConnStr.text()
        table_name = self.txtTableName.text()

        strEtc1 = self.txtEtc1.text().strip()
        strEtc2 = self.txtEtc2.text().strip()

        strWhere = " WHERE 1=1 "

        if  strEtc1 != '':
            strWhere = strWhere + " AND ETC1 = '{}'".format(strEtc1)

        if  strEtc2 != '':
            strWhere = strWhere + " AND ETC2 = '{}'".format(strEtc2)


        # 연결에 필요한 기본 정보 (유저, 비밀번호, 데이터베이스 서버 주소)
        con = cx_Oracle.connect(conn_str)
        cursor = con.cursor()


        sql = "delete from HAN.{} {}".format(table_name, strWhere)
        print(sql)
        cursor.execute(sql, ())
        cursor.execute("commit")




        out_Dir = self.txtConnStr.text()

        cnt = self.tblFiles.rowCount()

        # 상태 진행바
        self.progressBar.setRange(0, cnt)


        splitStr = self.cboSplit.currentText()

        if splitStr == '분할하지 않음': splitStr = None
        elif splitStr == 'Comma': splitStr = ','
        elif splitStr == 'Tab': splitStr = '\t'
        elif splitStr == 'Space': splitStr = ' '

        row = 0
        while True:

            cell = self.tblFiles.item(row, 1)
            dir_name = cell.text()

            cell = self.tblFiles.item(row, 0)
            file_name = cell.text()

            #pdfToOtherFormat(dir_name, file_name, out_Dir, toFileFormatNum, toFileFormatExt)
            insertToDB(cursor, dir_name, file_name, row, table_name, strEtc1, strEtc2, splitStr)
            row = row + 1
            # 상태 진행바
            self.progressBar.setValue(row)

            #종료조건
            if row >= cnt: break


        QMessageBox.information(self, '작업 종료', '작업이 종료되었습니다.', QMessageBox.Yes)



def insertToDB(cursor, dir_name, file_name, no, table_name, strEtc1, strEtc2, splitStr = None):
    full_file_name = os.path.join(dir_name, file_name)
    f = open(full_file_name, 'r') #, encoding='UTF8'

    lines = f.readlines()


    split_index = 0
    for line_no, contents in enumerate(lines):
        print(line_no, contents)
        contents = contents.strip()

        #분할하여 저장할 경우
        if splitStr != None:
            splitItems = contents.split(splitStr)
            for splitItem in splitItems:

                #공잭 제거
                splitItem = splitItem.strip()

                if splitItem == '': continue

                sql = "Insert into HAN.{}(no, file_name, line_no, split_index, contents, etc1, etc2) values(:1, :2, :3, :4, :5, :6, :7)".format((table_name))
                params = (no, file_name, line_no, split_index, splitItem, strEtc1, strEtc2)
                cursor.execute(sql, params)
                split_index = split_index +1
        else:
            sql = "Insert into HAN.{}(no, file_name, line_no, split_index, contents, etc1, etc2) values(:1, :2, :3, :4, :5, :6, :7)".format((table_name))
            params = (no, file_name, line_no, split_index, contents, strEtc1, strEtc2)
            cursor.execute(sql, params)



    if len(lines) > 0:
        cursor.execute("commit")

def search(list, dir_name, myExtend, findSubDir=True):
    file_names = os.listdir(dir_name)

    for file_name in file_names:
        full_filename = os.path.join(dir_name, file_name)
        # print(full_filename)
        if findSubDir and os.path.isdir(full_filename):
            search(list, full_filename, myExtend, findSubDir)

        else:
            ext = os.path.splitext(full_filename)[-1]
            if myExtend == '' or ext == myExtend:
                print('*************pdf 파일임...', full_filename)
                # pdfTohtml(dir_name, file_name)
                # wordTotxt(dir_name, file_name)
                list.append([dir_name, file_name])



if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    ex = CFileUploader()
    ex.show()
    sys.exit(app.exec_())
