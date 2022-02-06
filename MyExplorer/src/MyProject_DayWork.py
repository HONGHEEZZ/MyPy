from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic

import sys
import time
import datetime
import sqlite3
import pyperclip
import openpyxl
import os
import hashlib

my_dlg = uic.loadUiType("ui/MyProject_DayWork.ui")[0]

class CMyUiThread(QThread):
    finished = pyqtSignal(int)
    progressMsg = pyqtSignal(str)
    progressUI = pyqtSignal(object)


    def __init__(self, dir_name, ext):
        super().__init__()
        self.dir_name = dir_name
        self.ext = ext

        self.needStop = False
        self.MAX_RUN = 300



    def run(self):
        self.f_clear_directory(self.dir_name)
        
        self.f_capture()
        
        self.finished.emit(1) #총 수행건수 종료 시그널

    def f_get_file_hash(self, fname):
        f = open(fname, 'rb')
        my_data = f.read()
        f.close()

        m= hashlib.md5(my_data)

        hash_value = m.hexdigest()
        return hash_value


    def f_capture(self):
        from PIL import ImageGrab
        import pyautogui

        pyautogui.moveTo(300, 200, 1)
        pyautogui.click()

        old_hash_value = ''
        for i in range(self.MAX_RUN):
            if self.needStop:
                break

            time.sleep(1)
            img = ImageGrab.grab([0, 90, 1100, 900])
            fname = str(i).zfill(3)
            full_name = f"c:/capture/{fname}.png"
            img.save(full_name)

            pyautogui.press("down")
            pyautogui.press("pagedown")

            # 파일의 내용이 같으면 종료한다.
            new_hash_value = self.f_get_file_hash(full_name)
            if new_hash_value == old_hash_value:
                print("* Hash value 같음. 종료함.", new_hash_value)
                break

            old_hash_value = new_hash_value


    # ext : .png, .txt
    def f_clear_directory(self, dir_name, ext=None):
        file_list = os.listdir(dir_name)

        for file in file_list:
            file_name, file_ext = os.path.splitext(file)

            file_path = os.path.join(dir_name, file)
            if ext == None or file_ext == ext:
                os.remove(file_path)


class MyProject_DayWork(QDialog, my_dlg):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

        self.FILE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.BASE_DIR = os.path.join(self.FILE_DIR, "..\\")
        self.DB_FILE = os.path.join(self.BASE_DIR, "MyProject_DayWork.db")

        # DB 생성(오토 커밋)
        self.conn = sqlite3.connect(self.DB_FILE)

        # ui setup
        self.setupUi(self)

        self.setupUI()

        self.myid = 0
        self.strTableId = 'DayWork'

        self.myUiThread = None



    def setupUI(self):
        #최대화 버튼
        self.setWindowFlag(Qt.WindowMaximizeButtonHint)
        self.setWindowFlag(Qt.WindowMinimizeButtonHint)

        self.btnQuery.clicked.connect(self.btnQuery_Click)
        self.btnSave.clicked.connect(self.btnSave_Click)
        self.btnDelete.clicked.connect(self.btnDelete_Click)

        #상세 다음 순번 가져오기
        self.btnNextSeq.clicked.connect(self.btnNextSeq_Click)

        #상세 저장
        self.btnSaveDetail.clicked.connect(self.btnSaveDetail_Click)

        # 상세 삭제
        self.btnDeleteDetail.clicked.connect(self.btnDeleteDetail_Click)

        # 클릭
        self.tblFiles.clicked.connect(self.tblFiles_clicked)
        self.tblDetails.clicked.connect(self.tblDetails_clicked)

        # 선택 로우 변경시
        self.tblFiles.itemSelectionChanged.connect(self.tblFiles_clicked)
        self.tblDetails.itemSelectionChanged.connect(self.tblDetails_clicked)

        self.btnAddDetail.clicked.connect(self.btnAddDetail_Click)


        self.tblFiles.setColumnWidth(0, 120) #일자
        self.tblFiles.setColumnWidth(1, 60)  # 시간
        self.tblFiles.setColumnWidth(2, 250)  # 제목
        self.tblFiles.setColumnWidth(3, 100)  # 작업구분
        self.tblFiles.setColumnWidth(4, 100)  # 상태구분
        self.tblFiles.setColumnWidth(5, 60)  # To
        self.tblFiles.setColumnWidth(6, 200)  # contents
        self.tblFiles.setColumnWidth(7, 60)  # Etc1

        self.tblFiles.setSortingEnabled(True)

        self.tblDetails.setColumnWidth(0, 120)  # 일자
        self.tblDetails.setColumnWidth(1, 60)  # 시간
        self.tblDetails.setColumnWidth(2, 60)  # seq

        self.tblDetails.setColumnWidth(3, 200)  # 제목
        self.tblDetails.setColumnWidth(4, 100)  # 작업구분
        self.tblDetails.setColumnWidth(5, 100)  # 상태구분
        self.tblDetails.setColumnWidth(6, 60)  # To
        self.tblDetails.setColumnWidth(7, 200)  # contents
        self.tblDetails.setColumnWidth(8, 60)  # Etc1

        self.f_set_now()
        self.txtDay.setFocus()

        #job div
        self.cboJobDiv1.currentIndexChanged.connect(self.cboJobDiv1_IndexChanged)

        # db 테이블 지정
        self.f_setJobDiv1()

        #화면 로드시 조회하기
        self.btnQuery_Click()


        # Refresh 버튼
        self.btnRefresh.clicked.connect(self.btnRefresh_clicked)
        self.btnPaste.clicked.connect(self.btnPaste_clicked)



        self.btnGetXMLNode.clicked.connect(self.btnGetXMLNode_clicked)
        self.btnCaptureStart.clicked.connect(self.btnCaptureStart_clicked)
        self.btnCaptureStop.clicked.connect(self.btnCaptureStop_clicked)


    def f_init_uiThread(self):
        # 이미 생성되었으면 return
        if self.myUiThread:
            self.myUiThread.needStop = False #방어코드
            return

        #쓰레드 인스턴스 생성
        self.myUiThread = CMyUiThread('c:/capture', None)
        self.myUiThread.progressMsg.connect(self.f_uiThread_msg)
        self.myUiThread.progressUI.connect(self.f_uiThreadUI)
        self.myUiThread.finished.connect(self.f_uiThread_finished)


    def f_uiThread_msg(self):
        pass

    def f_uiThreadUI(self):
        pass

    def f_uiThread_finished(self):
        self.btnCaptureStart.setEnabled(True)
        self.btnCaptureStop.setEnabled(False)

    def btnCaptureStop_clicked(self):
        self.myUiThread.needStop = True

    def btnCaptureStart_clicked(self):
        #uiThread 초기화
        self.f_init_uiThread()
        self.myUiThread.start()

        self.btnCaptureStart.setEnabled(False)
        self.btnCaptureStop.setEnabled(True)

    def btnGetXMLNode_clicked(self):
        import xml.etree.ElementTree as et

        fname = QFileDialog.getOpenFileName(
            self, '파일 선택', '',
            '모든 파일 (*.*);')[0]

        if not fname:
            return

        # XML 파일 생성
        doc = et.parse(fname)

        # root 노드 얻기
        root = doc.getroot()

        full_str = ''

        # root 이하의 모든 자식의 태그명 프린트
        for parent in root.iter():
            for child in parent:

                str = child.tag + "$"
                if child.text:
                    str = str+child.text

                str = str + "$" + parent.tag

                my_node_list = list(child)
                my_len = len(my_node_list)

                if my_len == 0:
                    print(str)
                    str = str + '-'
                else:
                    str = str + "$leaf"

                full_str += str + '\n'
        QMessageBox.information(self, '알림', full_str, QMessageBox.Yes)

    def btnRefresh_clicked(self):
        # 우선 콘트롤 초기화
        self.f_init_controls()

        # * 시간 텍스트 박스에 현재시간 setting()
        self.f_set_now()

    def btnPaste_clicked(self):
        strClip = pyperclip.paste()

        print(strClip)

    # -----------------------------------------------------------------------------
    # * 상세 그리드 클릭시
    # -----------------------------------------------------------------------------
    def tblDetails_clicked(self):
        #한건도 없으면 종료
        rowCnt = self.tblDetails.rowCount()
        if rowCnt == 0:
            return
        
        # 현재 선택된 로우
        row = self.tblDetails.currentIndex().row()
        if row < 0:
            return

        strContents = self.tblDetails.item(row, 6).text()
        self.txtContents.setText(strContents)

        strDay = self.f_get_item_data(self.tblDetails, row, 0)
        strTime = self.f_get_item_data(self.tblDetails, row, 1)
        strSeq = self.f_get_item_data(self.tblDetails, row, 2)

        strTitle = self.f_get_item_data(self.tblDetails, row, 3)
        strWorkDiv = self.f_get_item_data(self.tblDetails, row, 4)
        strStatus = self.f_get_item_data(self.tblDetails, row, 5)
        strTo = self.f_get_item_data(self.tblDetails, row, 6)
        strWorkdContents = self.f_get_item_data(self.tblDetails, row, 7)
        strEtc1 = self.f_get_item_data(self.tblDetails, row, 8)

        # self.txtDay_2.setText(strDay)
        # self.txtTime_2.setText(strTime)
        self.txtSeq.setText(strSeq)

        self.txtTitle_2.setText(strTitle)
        self.cboWorkDiv_2.setCurrentText(strWorkDiv)
        self.cboStatus_2.setCurrentText(strStatus)
        self.txtTo_2.setText(strTo)
        self.txtContents_2.setText(strContents)
        self.txtEtc1_2.setText(strEtc1)

    # -------------------------------------------------------------------------
    # * * 콘트롤 초기화
    # -------------------------------------------------------------------------
    def f_init_controls(self):

        self.txtTitle.setText("")
        self.txtContents.setText("")
        self.tblDetails.setRowCount(0)
        self.txtContents.setText("")
        self.txtSeq.setText("")

        self.txtTitle_2.setText("")
        self.cboWorkDiv_2.setCurrentIndex(0)
        self.cboStatus_2.setCurrentIndex(0)
        self.txtTo_2.setText("")
        self.txtContents_2.setText("")
        self.txtEtc1_2.setText("")

    # -------------------------------------------------------------------------
    # * 메인그리드 클릭시
    # -------------------------------------------------------------------------
    def tblFiles_clicked(self):

        # 우선 콘트롤 초기화
        self.f_init_controls()


        row = self.tblFiles.currentIndex().row()

        if row < 0:
            return

        strContents = self.tblFiles.item(row, 6).text()
        self.txtContents.setText(strContents)


        strDay = self.f_get_item_data(self.tblFiles, row, 0)
        strTime = self.f_get_item_data(self.tblFiles, row, 1)
        strTitle = self.f_get_item_data(self.tblFiles, row, 2)
        strWorkDiv = self.f_get_item_data(self.tblFiles, row, 3)
        strStatus = self.f_get_item_data(self.tblFiles, row, 4)
        strTo = self.f_get_item_data(self.tblFiles, row, 5)
        strWorkdContents = self.f_get_item_data(self.tblFiles, row, 6)
        strEtc1 = self.f_get_item_data(self.tblFiles, row, 7)

        self.txtDay.setText(strDay)
        self.txtTime.setText(strTime)
        self.txtTitle.setText(strTitle)
        self.cboWorkDiv.setCurrentText(strWorkDiv)
        self.cboStatus.setCurrentText(strStatus)
        self.txtTo.setText(strTo)
        self.txtContents.setText(strContents)
        self.txtEtc1.setText(strEtc1)

        #------------------------------------------------------------------------------
        #* 상세 그리드 보여주기
        # ------------------------------------------------------------------------------
        self.f_query_details(strDay, strTime)

    def f_query_details(self, strDay, strTime):
        self.tblDetails.setRowCount(0)

        # 1. db에서 읽어온다.
        cursor = self.conn.cursor()
        sql = f"""
                        SELECT WorkDay,
                               WorkTime,
                               seq || '' as seq,
                               WorkTitle,
                               WorkDiv,
                               WorkStatus,
                               WorkTo,
                               WorkContents,
                               WorkEtc1
                          FROM DayWorkDetails
                         WHERE WorkDay = ?
                           AND WorkTime = ?
                         ORDER BY WorkDay, WorkTime, seq desc
                    """

        cursor.execute(sql, (strDay, strTime))
        rows = cursor.fetchall()

        if rows == None or len(rows) == 0:
            msg = f"[MyProject_DayWork.db의 DayWorkDetails 테이블에 저장된 데이터가 없습니다."
            #QMessageBox.information(self, '알림', msg, QMessageBox.Yes)
            return

        colCount = len(rows[0])

        for row in rows:
            myArg = [] #여기서 초기화 해야 한다.
            for idx in range(colCount):
                myArg.append(row[idx])

            # 그리드에 추가하기
            self.f_addFileAtBottom(myArg, self.tblDetails)

        cursor.close()

        # -----------------------------------------------------------------------------
        # * 작업하던 로우 다시 조회하기
        # -----------------------------------------------------------------------------
        intRow = self.f_find_details()
        self.tblDetails.selectRow(intRow)

    # -----------------------------------------------------------------------------
    # * 작업하던 로우 찾기
    # -----------------------------------------------------------------------------
    def f_find_details(self):
        strSeq = self.txtSeq.text()
        intFindRow = 0

        rowCount = self.tblDetails.rowCount()
        for row in range(rowCount):
            seq = self.f_get_item_data(self.tblDetails, row, 2)

            if strSeq == seq:
                intFindrow = row
                break

        return intFindRow


    def cboJobDiv1_IndexChanged(self):
        self.f_setJobDiv1()
        self.btnQuery_Click()

    def f_setJobDiv1(self):
        self.jobDiv = self.cboJobDiv1.currentText()
        self.strTableId = ''
        if self.jobDiv == "01.DayWork":
            self.strTableId = "DayWork"
        elif self.jobDiv == "02.ToDoList":
            self.strTableId = "ToDoList"



    def f_set_now(self):
        #로딩시 오늘을 기본값으로 넣어줌
        strToday = datetime.datetime.today().strftime("%Y-%m-%d")
        self.txtDay.setText(strToday)

        strTime = datetime.datetime.today().strftime("%H:%M:%S")
        self.txtTime.setText(strTime)

    # -----------------------------------------------------------------------------
    # * Master 저장
    # -----------------------------------------------------------------------------
    def btnSave_Click(self):
        strDay = self.txtDay.text()
        strTime = self.txtTime.text()
        strTitle = self.txtTitle.text()
        strWorkDiv = self.cboWorkDiv.currentText()
        strStatus = self.cboStatus.currentText()
        strTo = self.txtTo.text()
        strWorkContents = self.txtContents.toPlainText()
        strEtc1 = self.txtEtc1.text()

        myArg = [strDay, strTime, strTitle, strWorkDiv, strStatus,
                 strTo, strWorkContents, strEtc1]

        #커서 획득
        cursor = self.conn.cursor()

        #db에 저장하기
        self.f_saveMaster(cursor, myArg)


        cursor.close()
        self.conn.commit()

        # 다시 조회
        self.btnQuery_Click()

    # -----------------------------------------------------------------------------
    # * Detail 저장
    # -----------------------------------------------------------------------------
    def btnSaveDetail_Click(self):

        strDay = self.txtDay.text()
        strTime = self.txtTime.text()
        strSeq = self.txtSeq.text()

        strTitle = self.txtTitle_2.text()
        strWorkDiv = self.cboWorkDiv_2.currentText()
        strStatus = self.cboStatus_2.currentText()
        strTo = self.txtTo_2.text()
        strWorkContents = self.txtContents_2.toPlainText()
        strEtc1 = self.txtEtc1_2.text()

        # -----------------------------------------------------------------------------
        # * 순번 입력 필수
        # -----------------------------------------------------------------------------
        if strSeq == '':
            QMessageBox.warning(self, '순번 입력 필수', '순번을 입력 후 저장하세요.', QMessageBox.Yes)
            self.btnNextSeq.setFocus()
            return

        # -----------------------------------------------------------------------------
        # * 제목 입력 필수
        # -----------------------------------------------------------------------------
        if strTitle == '':
            QMessageBox.warning(self, ' 제목 입력 필수', '제목을 입력 후 저장하세요.', QMessageBox.Yes)
            self.txtTitle_2.setFocus()
            return

        myArg = [strDay, strTime, strSeq, strTitle, strWorkDiv, strStatus,
                 strTo, strWorkContents, strEtc1]

        # 커서 획득
        cursor = self.conn.cursor()

        # db에 저장하기
        self.f_saveDetails(cursor, myArg)

        cursor.close()
        self.conn.commit()

        # 상세 다시 조회
        self.f_query_details(strDay, strTime)



    def btnAddDetail_Click(self):
        rowCount = self.tblDetails.rowCount()
        self.tblDetails.setRowCount(rowCount + 1)

        # pk 추가하기
        strDay = self.txtDay.text()
        strTime = self.txtTime.text()
        rowPosition = rowCount
        strSeq = str(rowPosition + 1) #db 저장은 1번부터 하자.

        item = QTableWidgetItem(strDay)
        self.tblDetails.setItem(rowPosition, 0, item)

        item = QTableWidgetItem(strTime)
        self.tblDetails.setItem(rowPosition, 1, item)

        item = QTableWidgetItem(strSeq)
        self.tblDetails.setItem(rowPosition, 2, item)

    # -----------------------------------------------------------------------------
    # * Detail 삭제
    # -----------------------------------------------------------------------------
    def btnDeleteDetail_Click(self):


        strDay = self.txtDay.text()
        strTime = self.txtTime.text()
        strSeq = self.txtSeq.text()


        # -----------------------------------------------------------------------------
        # * 삭제 확인
        # -----------------------------------------------------------------------------
        # 삭제 확인
        ret = QMessageBox.question(self, '확인', f'선택된 [{strSeq}] 순번을 삭제하시겠습니까?')
        if ret == QMessageBox.No: return

        myArg = [strDay, strTime, strSeq]


        #커서 획득
        cursor = self.conn.cursor()

        # db에 저장하기
        self.f_deleteDetails(cursor, myArg)

        cursor.close()
        self.conn.commit()

        #상세 다시 조회
        self.f_query_details(strDay, strTime)


    # -----------------------------------------------------------------------------
    #* 상세 다음 순번 가져오기
    # -----------------------------------------------------------------------------
    def btnNextSeq_Click(self):
        rowCount = self.tblDetails.rowCount()

        if rowCount == 0:
            self.txtSeq.setText("1")
            return

        #row는 zero base임.
        strLastSeq = self.f_get_item_data(self.tblDetails, rowCount-1, 2)

        intLastSeq = int(strLastSeq) + 1
        strLastSeq = str(intLastSeq)

        self.txtSeq.setText(strLastSeq)

        self.txtTitle_2.setText("")
        self.txtTo_2.setText("")
        self.txtContents_2.setText("")
        self.txtEtc1_2.setText("")


    def f_saveMaster(self, cursor, myArg):

        strMsg = ''

        #우선 있는지 확인
        sql = f"""
                select count(1)
                  from {self.strTableId}
                 where WorkDay = ?
                   and WorkTime = ?
            """
        cursor.execute(sql, (myArg[0], myArg[1]))

        row = cursor.fetchone()

        sql = ""
        if row[0] == 0:
            sql = f"""
                INSERT INTO {self.strTableId} (WorkDay, WorkTime, WorkTitle, WorkDiv, WorkStatus, WorkTo, WorkContents, WorkEtc1)
                values(?, ?, ?, ?, ?, ?, ?, ?)
            """
            cursor.execute(sql, myArg)

            strMsg = '1건이 저장되었습니다.'
        else:
            sql = f"""
                    update {self.strTableId}
                    set 
                        
                        WorkTitle	 = ?, 
                        WorkDiv	 = ?, 
                        WorkStatus	 = ?, 
                        WorkTo	 = ?, 
                        WorkContents	 = ?, 
                        WorkEtc1	 = ?
                  where WorkDay	 = ? 
                    and WorkTime	 = ?
            """

            cursor.execute(sql, [myArg[2],
                                 myArg[3],
                                 myArg[4],
                                 myArg[5],
                                 myArg[6],
                                 myArg[7],
                                 myArg[0],
                                 myArg[1]
                                 ])

            strMsg = '1건이 수정되었습니다.'

        QMessageBox.information(self, "확인", strMsg, QMessageBox.Ok)

    def f_get_item_data(self, tblWidget, row, col):
        rtn = ''
        item = tblWidget.item(row, col)
        if item != None:
            rtn = item.text()
        return rtn

    # -----------------------------------------------------------------------------
    # * 상세 삭제
    # -----------------------------------------------------------------------------
    def f_deleteDetails(self, cursor, myArg):
        # 무조건 삭제 후 저장
        sql = f"""
                        delete
                          from DayworkDetails
                         where WorkDay = ?
                           and WorkTime = ?
                           and seq = ?
                    """
        cursor.execute(sql, (myArg[0], myArg[1], myArg[2]))

        if cursor.rowcount != 1:
            QMessageBox.warning(self, '오류', f"[{cursor.rowcount}]건이 삭제됨. 삭제 오류 발생.", QMessageBox.Yes)

    # -----------------------------------------------------------------------------
    # * 상세 저장
    # -----------------------------------------------------------------------------
    def f_saveDetails(self, cursor, myArg):
        # 무조건 삭제 후 저장
        strMsg = ''

        # 우선 있는지 확인
        sql = f"""
                delete
                  from DayworkDetails
                 where WorkDay = ?
                   and WorkTime = ?
                   and seq = ?
            """
        cursor.execute(sql, (myArg[0], myArg[1], myArg[2]))


        strDay = myArg[0]
        strTime = myArg[1]
        strSeq = myArg[2]
        strTitle = myArg[3]
        strWorkDiv = myArg[4]
        strStatus = myArg[5]
        strTo = myArg[6]
        strWorkContents = myArg[7]
        strEtc1 = myArg[8]

        intSeq = int(strSeq)

        sql = ""
        sql = f"""
                        INSERT INTO DayWorkDetails (WorkDay, WorkTime, seq, WorkTitle, WorkDiv, WorkStatus, WorkTo, WorkContents, WorkEtc1)
                        values(?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """
        cursor.execute(sql, (strDay, strTime, intSeq, strTitle, strWorkDiv, strStatus, strTo,
                             strWorkContents, strEtc1))

    def btnQuery_Click(self):
        self.tblFiles.setRowCount(0)

        self.txtSeq.setText("")

        # 1. db에서 읽어온다.
        cursor = self.conn.cursor()
        sql = f"""
                SELECT WorkDay,
                       WorkTime,
                       WorkTitle,
                       WorkDiv,
                       WorkStatus,
                       WorkTo,
                       WorkContents,
                       WorkEtc1
                  FROM {self.strTableId}
                 ORDER BY WorkDay desc, WorkTime desc
            """

        cursor.execute(sql)
        rows = cursor.fetchall()

        if rows == None or len(rows) == 0:
            msg = f"[MyProject_DayWork.db의 {self.strTableId} 테이블에 저장된 데이터가 없습니다."
            QMessageBox.information(self, '알림', msg, QMessageBox.Yes)
            return


        for row in rows:
            myArg = []
            for idx in range(8):
                myArg.append(row[idx])


            #그리드에 추가하기
            self.f_addFileAtBottom(myArg, self.tblFiles)

        cursor.close()
        self.tblFiles.repaint()

    def f_addFileAtBottom(self, myArg, myWidget):
        rowPosition = 0 #self.tblFiles.rowCount()+1
        myWidget.insertRow(rowPosition)

        colCount = myWidget.columnCount()
        for i in range(colCount):
            item = QTableWidgetItem(myArg[i])
            myWidget.setItem(rowPosition, i, item)

        #속도가 너무 느려 주석처리함.
        #myWidget.repaint()

        #* 새로 추가되는 아이템이 화면에 보이게 처리
        #myWidget.scrollToItem(item)
        #myWidget.selectRow(rowPosition)

    def btnDelete_Click(self):


        strDay = self.txtDay.text()
        strTime = self.txtTime.text()
        strTitle = self.txtTitle.text()
        strWorkDiv = self.cboWorkDiv.currentText()
        strStatus = self.cboStatus.currentText()
        strTo = self.txtTo.text()
        strWorkContents = self.txtContents.toPlainText()
        strEtc1 = self.txtEtc1.text()

        # 삭제 확인
        ret = QMessageBox.question(self, '확인', f'선택된 [{strTitle}] 내용을 삭제하시겠습니까?')
        if ret == QMessageBox.No: return

        myArg = [strDay, strTime, strTitle, strWorkDiv, strStatus,
                 strTo, strWorkContents, strEtc1]

        #db에 저장하기
        self.f_deleteToDB(myArg)

        # 다시 조회
        self.btnQuery_Click()


    def f_deleteToDB(self, myArg):


        # 1. db에서 읽어온다.
        cursor = self.conn.cursor()
        sql = f"""
                    delete from {self.strTableId}
                      where WorkDay = ?
                        and WorkTime = ?
                """
        cursor.execute(sql, (myArg[0], myArg[1]))

        if cursor.rowcount == 1:
            QMessageBox.information(self, '성공', "1건이 정상 삭제되었습니다.", QMessageBox.Yes)
        else:
            QMessageBox.critical(self, '실패', f"처리건수가 {cursor.rowcount}건임. 처리건수는 1건이어야 함.")

        sql = f"""
                            delete from DayWorkDetails
                              where WorkDay = ?
                                and WorkTime = ?
                        """
        cursor.execute(sql, (myArg[0], myArg[1]))


        cursor.close()
        self.conn.commit()

if __name__ == "__main__":
    import sys

    app = QApplication(sys.arg)
    dlg = MyProject_DayWork()
    dlg.exec_()