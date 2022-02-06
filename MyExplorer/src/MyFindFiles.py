import sys

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic
import os
import time

import enum

import threading

my_dlg = uic.loadUiType("ui/MyFindFiles.ui")[0]

class JOB_TYPE(enum.Enum):
    FIND_BY_NAME = 0
    FIND_BY_CONTENTS = 1

class FindFiles(QThread):
    finished = pyqtSignal(int)
    progressMsg = pyqtSignal(str)
    progressUI = pyqtSignal(object)

    def __init__(self, job_type, search_folder, search_str):
        super().__init__()
        self.job_type = job_type
        self.search_folder = search_folder
        self.search_str = search_str

        self.needStop = False


    def run(self):

        if self.job_type == JOB_TYPE.FIND_BY_NAME:
            cnt_tot = self.f_findByName(self.search_folder, self.search_str)

            self.finished.emit(cnt_tot) #총 수행건수 종료시그널...

        elif self.job_type == JOB_TYPE.FIND_BY_CONTENTS:
            cnt_tot = self.f_findByContents(self.search_folder, self.search_str)
            self.finished.emit(cnt_tot)  # 총 수행건수 종료시그널...

    def f_findByContents(self, search_folder, search_str):
        print("***********f_findByContents")

        import os
        import chardet
        import mimetypes

        search_str = search_str.lower()

        cnt_dir = 0
        cnt_files = 0
        cnt_found = 0

        for curdir, dirs, files in os.walk(search_folder):

            if self.needStop: break
            self.progressMsg.emit(f"{curdir}")

            cnt_dir += 1

            for fname in files:
                fpath = os.path.join(curdir, fname)
                mime = mimetypes.guess_type(fpath)
                cnt_files += 1

                if self.needStop: break
                self.progressMsg.emit(f"{curdir} {fname}")

                print(fname)


                if not mime[0]:
                    print(fname, '***** CONTINUE.... Mime : ', mime)
                    continue
                elif mime[0].startswith('application'):
                    pass
                elif mime[0].startswith('text'):
                    pass
                else:
                    print(fname, '***** CONTINUE.... Mime : ', mime)
                    continue    #텍스트 파일이 아니면 통과

                print("* 파일 읽기 시작****")
                content = open(fpath, 'rb').read(1000) #파일 읽기
                encoding = chardet.detect(content)['encoding']
                print("* 파일 읽기 종료****")
                print(fname, " : ", encoding)

                try:
                    print("*** str변환 직전...")
                    txt = str(content, encoding) #str로 변환.
                    print("*** str변환 직후...")
                except:
                    print(fname, " : ", encoding, " ----> 변환 실패...")
                    continue

                if search_str in txt.lower():
                    print(fpath)
                    self.progressUI.emit(('File', curdir, fname))


                cnt_found += 1

        # 작업 종료 내용 표시...
        cnt_tot = cnt_dir + cnt_files
        self.progressMsg.emit(f"총 폴더[{cnt_dir}]개, 파일 [{cnt_files}]개 중 [{cnt_found}]개 찾음.")

        return cnt_tot


    def f_findByName(self, search_folder, search_str):

        search_str = search_str.lower()


        cnt_dir = 0
        cnt_files = 0
        cnt_found = 0
        for curdir, dirs, files in os.walk(search_folder):
            if self.needStop: break

            self.progressMsg.emit(f"{curdir}")

            cnt_dir += 1

            # 새로운 폴더가 대상인지체크...
            if curdir.lower().find(search_str) >= 0:
                self.progressUI.emit(('Dir', curdir, ''))
                cnt_found += 1

            time.sleep(0.001)
            for fname in files:

                cnt_files += 1
                if self.needStop: break

                self.progressMsg.emit(f"{curdir} {fname}")

                if fname.lower().find(search_str) >= 0:
                    self.progressUI.emit(('File', curdir, fname))
                    cnt_found += 1

        #작업 종료 내용 표시...
        cnt_tot = cnt_dir + cnt_files
        self.progressMsg.emit(f"총 폴더[{cnt_dir}]개, 파일 [{cnt_files}]개 중 [{cnt_found}]개 찾음.")

        return cnt_tot

class MyFindFiles(QDialog, my_dlg):
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

        #확인해보기를 누르기 전까지는 OK 버튼은 비 활성화
        self.btnOk.setEnabled(False)
        
        
        self.tblFiles.setColumnWidth(0, 30)   # 선택
        self.tblFiles.setColumnWidth(1, 60)  # 선택
        self.tblFiles.setColumnWidth(2, 250)  # AS-IS
        self.tblFiles.setColumnWidth(3, 250)  # TO-BE

        self.tblFiles.setSortingEnabled(True)

        #doWork
        self.btnDoWork.clicked.connect(self.btnDoWork_Click)
        self.btnOk.clicked.connect(self.btnOk_Click)

        #Stop 버튼
        self.btnStop.clicked.connect(self.btnStop_Click)


        # 체크박스
        self.chkAll.clicked.connect(self.chkAll_Click)
        self.chkAll.setChecked(True)

        self.txtSearchKey.returnPressed.connect(self.txtSearchKey_returnPressed)

        self.txtSearchKey.setFocus()

        self.cboWork.setCurrentIndex(1)


        #오른쪽 마우스 클릭
        # 컨텍스트 메뉴
        self.tblFiles.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tblFiles.customContextMenuRequested.connect(self.on_tblFiles_contextMenu)


    def on_tblFiles_contextMenu(self, position):

        it = self.tblFiles.itemAt(position)
        if it is None: return
        r = it.row()
        c = it.column()
        #item_range = QTableWidgetSelectionRange(0, c, self.tblFiles.rowCount() - 1, c)
        #self.tblFiles.setRangeSelected(item_range, True)

        menu = QMenu()

        action_empty = open_folder_action = open_calc = None

        if not self.tblFiles.indexAt(position).isValid():
            action_empty = menu.addAction(self.tr("Empty Area..."))
        else:
            open_folder_action = menu.addAction("Open Folder with Explorer")
            open_calc = menu.addAction("Open Calc")
            open_file = menu.addAction("파일 열기")

        action = menu.exec_(self.tblFiles.viewport().mapToGlobal(position))


        if action == action_empty:
            print("action empty...")

        if action == open_calc:
            from subprocess import Popen
            Popen('calc')

        elif action == open_file:
            dir = self.tblFiles.item(r, 2).text()
            fname = self.tblFiles.item(r, 3).text()
            fpath = os.path.join(dir, fname)

            os.startfile(fpath)

        elif action == open_folder_action:
            print("zzzzzzzzzz")
            item = self.tblFiles.item(r, 2)
            fpath = item.text()

            os.startfile(fpath)


    # ------------------------------------------------------------------------------
    # * 전체 선택 / 해제
    # ------------------------------------------------------------------------------
    def chkAll_Click(self):
        print("******checked.....")
        if len(self.m_checkBox) == 0: return

        value = self.chkAll.isChecked()
        for chk in self.m_checkBox:
            chk.setChecked(value)

    def txtSearchKey_returnPressed(self):
        self.btnDoWork_Click()

    def setUrl(self, fpath):
        self.txtUrl.setText(fpath)
        self.fpath = fpath

    
    
    def insertCheckBoxToTable(self):

        self.numRow = self.tblFiles.rowCount()
        for i in range(self.numRow):
            ckbox = QCheckBox()
            ckbox.setChecked(True)
            self.m_checkBox.append(ckbox)

        for i in range(self.numRow):
            cellWidget = QWidget()
            layoutCB = QHBoxLayout(cellWidget)
            layoutCB.addWidget(self.m_checkBox[i])
            layoutCB.setAlignment(Qt.AlignCenter)
            layoutCB.setContentsMargins(0, 0, 0, 0)
            cellWidget.setLayout(layoutCB)

            # self.tableWidget.setCellWidget(i,0,self.checkBoxList[i])
            self.tblFiles.setCellWidget(i, 0, cellWidget)

    def f_addFileAtBottom(self, strDiv, fpath, fname):

        rowPosition = self.tblFiles.rowCount()
        self.tblFiles.insertRow(rowPosition)

        item = QTableWidgetItem(strDiv)

        self.tblFiles.setItem(rowPosition, 1,item)
        self.tblFiles.setItem(rowPosition, 2, QTableWidgetItem(fpath))
        self.tblFiles.setItem(rowPosition, 3, QTableWidgetItem(fname))

        #self.tblFiles.repaint()

        # ------------------------------------------------------------------------------
        # * 새로 추가되는 아이템이 화면에 보이게 처리....
        # ------------------------------------------------------------------------------
        self.tblFiles.scrollToItem(item)
        self.tblFiles.selectRow(rowPosition+1)

    def f_findFiles_UI(self, myTuple):

        strDiv = myTuple[0]
        curdir = myTuple[1]
        fname = myTuple[2]

        self.f_addFileAtBottom(strDiv, curdir, fname)


    def f_findFiles_msg(self, str):

        self.lblMsg.setText(f"{str}")
        #self.lblMsg.repaint()

    def f_findFiles_finished(self, cnt_tot):
        print('* f_findFiles_finished *******************')
        self.btnDoWork.setEnabled(True)
        self.btnStop.setEnabled(False)

    def btnStop_Click(self):
        self.threadFindFiles.needStop = True


    def btnDoWork_Click(self):
        index = self.cboWork.currentIndex()
        self.tblFiles.setRowCount(0)

        #------------------------------------------------------------------------------
        #* 파일명 찾기
        #------------------------------------------------------------------------------
        if index == 0:
            search_folder = self.txtUrl.text()
            search_str = self.txtSearchKey.text()

            # 쓰레드 인스턴스 생성
            self.threadFindFiles = FindFiles(JOB_TYPE.FIND_BY_NAME ,search_folder, search_str)

            self.threadFindFiles.progressMsg.connect(self.f_findFiles_msg)
            self.threadFindFiles.progressUI.connect(self.f_findFiles_UI)
            self.threadFindFiles.finished.connect(self.f_findFiles_finished)

            self.threadFindFiles.start()

            self.btnDoWork.setEnabled(False)
            self.btnStop.setEnabled(True)

        # ------------------------------------------------------------------------------
        # * 내용으로 찾기...
        # ------------------------------------------------------------------------------
        elif index == 1:


            search_folder = self.txtUrl.text()
            search_str = self.txtSearchKey.text()

            # 쓰레드 인스턴스 생성
            self.threadFindFiles = FindFiles(JOB_TYPE.FIND_BY_CONTENTS, search_folder, search_str)

            self.threadFindFiles.progressMsg.connect(self.f_findFiles_msg)
            self.threadFindFiles.progressUI.connect(self.f_findFiles_UI)
            self.threadFindFiles.finished.connect(self.f_findFiles_finished)

            self.threadFindFiles.start()

            self.btnDoWork.setEnabled(False)
            self.btnStop.setEnabled(True)




    def btnOk_Click(self):
        os.chdir(self.fpath)

        for row, chk in enumerate(self.m_checkBox):
            if chk.isChecked():
                cell = self.tblFiles.item(row, 2)
                file = cell.text()

                cell = self.tblFiles.item(row, 3)
                file2 = cell.text()

                os.rename(file, file2)

                self.close()

        QMessageBox.information(self, '변경 완료', f"* 총 [{row+1}]건 변경완료")
    
if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    dlg = MyFindFiles()
    dlg.exec_()
