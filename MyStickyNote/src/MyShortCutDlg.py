from PyQt5.QtWidgets import QDialog, QGroupBox, QCheckBox, QTableWidget, QVBoxLayout, QHBoxLayout, QSplitter, QLineEdit, \
                            QPushButton, QLabel, QComboBox, QMessageBox, QTableWidgetItem
from PyQt5.QtCore import Qt
from PyQt5 import uic


import os
import sqlite3

my_dlg = uic.loadUiType("ui/MyClipboard.ui")[0]

class MyShortCutDlg(QDialog, my_dlg):
    def __init__(self):
        super().__init__()

        self.FILE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.BASE_DIR = os.path.join(self.FILE_DIR, "..\\")
        self.DB_FILE = os.path.join(self.BASE_DIR, "MyShortCut.db")

        # DB 생성(오토 커밋)
        self.conn = sqlite3.connect(self.DB_FILE)


        self.setupUi(self)
        self.setupUI()

        self.f_query()

    def setupUI(self):

        self.btnQuery.clicked.connect(self.btnQuery_Click)
        self.btnSave.clicked.connect(self.btnSave_Click)
        self.btnDelete.clicked.connect(self.btnDelete_Click)


        # 상세 다음 순번 가져오기
        self.btnNextSeq.clicked.connect(self.btnNextSeq_Click)

        # 클릭
        self.tblFiles.clicked.connect(self.tblFiles_clicked)
        #선택로우 변경시
        self.tblFiles.itemSelectionChanged.connect(self.tblFiles_clicked)

        self.tblFiles.setColumnWidth(0, 60)  # seq
        self.tblFiles.setColumnWidth(1, 120)  # Title
        self.tblFiles.setColumnWidth(2, 120)  # ScDiv

        self.tblFiles.setColumnWidth(3, 200)  # doaction
        self.tblFiles.setColumnWidth(4, 100)  # Alt
        self.tblFiles.setColumnWidth(5, 100)  # Ctrl
        self.tblFiles.setColumnWidth(6, 60)  # shift
        self.tblFiles.setColumnWidth(7, 200)  # shortCut
        self.tblFiles.setColumnWidth(8, 60)  # Etc1

    # -----------------------------------------------------------------------------
    # * 상세 그리드 클릭시
    # -----------------------------------------------------------------------------
    def tblFiles_clicked(self):
        # 한건도 없으면 종료
        rowCnt = self.tblFiles.rowCount()
        if rowCnt == 0:
            return

        # 현재 선택된 로우
        row = self.tblFiles.currentIndex().row()
        if row < 0:
            return


        strSeq = self.f_get_item_data(self.tblFiles, row, 0)

        strTitle = self.f_get_item_data(self.tblFiles, row, 1)
        strScDiv = self.f_get_item_data(self.tblFiles, row, 2)
        strDoAction = self.f_get_item_data(self.tblFiles, row, 3)

        strAlt = self.f_get_item_data(self.tblFiles, row, 4)
        strCtrl = self.f_get_item_data(self.tblFiles, row, 5)
        strShift = self.f_get_item_data(self.tblFiles, row, 6)
        strShortCut = self.f_get_item_data(self.tblFiles, row, 7)

        # self.txtDay_2.setText(strDay)
        # self.txtTime_2.setText(strTime)
        self.txtSeq.setText(strSeq)

        self.txtTitle.setText(strTitle)
        self.cboScDiv.setCurrentText(strScDiv)
        self.txtDoActions.setText(strDoAction)
        self.chkAlt.setChecked(int(strAlt))
        self.chkCtrl.setChecked(int(strCtrl))
        self.chkShift.setChecked(int(strShift))
        self.txtShortCut.setText(strShortCut)



    def btnQuery_Click(self):
        self.f_query()

    def f_query(self):
        self.tblFiles.setRowCount(0)

        # 1. db에서 읽어온다.
        cursor = self.conn.cursor()
        sql = f"""
                SELECT seq|| '',
                        Title	 , 
                        ScDiv	 , 
                        doAction	 , 
                        Alt	|| '' , 
                        Ctrl|| ''	 ,
                        Shift|| ''	 ,
                        ShortCut	 
                  FROM MyShortCut
                 ORDER BY 1 desc
        """

        cursor.execute(sql)
        rows = cursor.fetchall()

        if rows == None or len(rows) == 0:
            msg = f"[MyProject_DayWork.db의 DayWorkDetails 테이블에 저장된 데이터가 없습니다."
            # QMessageBox.information(self, '알림', msg, QMessageBox.Yes)
            return

        colCount = len(rows[0])

        for row in rows:
            myArg = []  # 여기서 초기화 해야 한다.
            for idx in range(colCount):
                myArg.append(row[idx])

            # 그리드에 추가하기
            self.f_addFileAtBottom(myArg, self.tblFiles)

        cursor.close()

        # -----------------------------------------------------------------------------
        # * 작업하던 로우 다시 조회하기
        # -----------------------------------------------------------------------------
        intRow = self.f_find_row()
        self.tblFiles.selectRow(intRow)

    def f_addFileAtBottom(self, myArg, myWidget):
        rowPosition = 0 #self.tblFiles.rowCount()+1
        myWidget.insertRow(rowPosition)

        colCount = myWidget.columnCount()
        for i in range(colCount):
            item = QTableWidgetItem(myArg[i])
            myWidget.setItem(rowPosition, i, item)

        # 속도가 너무 느려 주석처리함.
        # myWidget.repaint()

        # * 새로 추가되는 아이템이 화면에 보이게 처리
        # myWidget.scrollToItem(item)
        # myWidget.selectRow(rowPosition)
    # -----------------------------------------------------------------------------
    # * 작업하던 로우 찾기
    # -----------------------------------------------------------------------------
    def f_find_row(self):
        strSeq = self.txtSeq.text()
        intFindRow = 0

        rowCount = self.tblFiles.rowCount()
        for row in range(rowCount):
            seq = self.f_get_item_data(self.tblFiles, row, 0)

            if strSeq == seq:
                intFindRow = row
                break

        return intFindRow
    
    def btnSave_Click(self):


        strSeq = self.txtSeq.text()

        strTitle = self.txtTitle.text()
        strScDiv = self.cboScDiv.currentText()
        strdoAction = self.txtDoActions.text()
        strAlt = self.chkAlt.isChecked()
        strCtrl = self.chkCtrl.isChecked()
        strShift = self.chkShift.isChecked()
        strShortCut = self.txtShortCut.text()

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
            self.txtTitle.setFocus()
            return

        myArg = [strSeq, strTitle, strScDiv, strdoAction, strAlt, strCtrl, strShift, strShortCut]

        # 커서 획득
        cursor = self.conn.cursor()

        # db에 저장하기
        self.f_save(cursor, myArg)

        cursor.close()
        self.conn.commit()

        # 다시 조회
        self.btnQuery_Click()

    def btnDelete_Click(self):
        strSeq = self.txtSeq.text()

        # -----------------------------------------------------------------------------
        # * 삭제 확인
        # -----------------------------------------------------------------------------
        # 삭제 확인
        ret = QMessageBox.question(self, '확인', f'선택된 [{strSeq}] 순번을 삭제하시겠습니까?')
        if ret == QMessageBox.No: return

        myArg = [strSeq]

        # 커서 획득
        cursor = self.conn.cursor()

        # db에 저장하기
        self.f_delete(cursor, myArg)

        cursor.close()
        self.conn.commit()

        # 상세 다시 조회
        self.f_query()

    # -----------------------------------------------------------------------------
    # * 상세 삭제
    # -----------------------------------------------------------------------------
    def f_delete(self, cursor, myArg):
        # 무조건 삭제 후 저장
        sql = f"""
                        delete
                          from MyShortCut
                         where 1=1
                           and seq = ?
                    """
        cursor.execute(sql, (myArg[0],))

        if cursor.rowcount != 1:
            QMessageBox.warning(self, '오류', f"[{cursor.rowcount}]건이 삭제됨. 삭제 오류 발생.", QMessageBox.Yes)

    def f_save(self, cursor, myArg):

        strMsg = ''

        # 우선 있는지 확인
        sql = f"""
                select count(1)
                  from MyShortCut
                 where seq = ?
            """
        cursor.execute(sql, (myArg[0],))

        row = cursor.fetchone()

        sql = ""
        if row[0] == 0:
            sql = f"""
                INSERT INTO MyShortCut (Seq, Title, ScDiv, doAction, Alt, Ctrl, Shift, ShortCut)
                values(?, ?, ?, ?, ?, ?, ?, ?)
            """
            cursor.execute(sql, myArg)

            strMsg = '1건이 저장되었습니다.'
        else:
            sql = f"""
                    update MyShortCut
                    set 
                        Title	 = ?, 
                        ScDiv	 = ?, 
                        doAction	 = ?, 
                        Alt	 = ?, 
                        Ctrl	 = ?,
                        Shift	 = ?,
                        ShortCut	 = ?
                  where Seq	 = ? 
            """

            cursor.execute(sql, [myArg[1],
                                 myArg[2],
                                 myArg[3],
                                 myArg[4],
                                 myArg[5],
                                 myArg[6],
                                 myArg[7],
                                 myArg[0]
                                 ])

            strMsg = '1건이 수정되었습니다.'

        QMessageBox.information(self, "확인", strMsg, QMessageBox.Ok)

    # -----------------------------------------------------------------------------
    # * 상세 다음 순번 가져오기
    # -----------------------------------------------------------------------------
    def btnNextSeq_Click(self):
        rowCount = self.tblFiles.rowCount()

        if rowCount == 0:
            self.txtSeq.setText("1")
            return

        # row는 zero base임.
        strLastSeq = self.f_get_item_data(self.tblFiles, rowCount - 1, 0)

        intLastSeq = int(strLastSeq) + 1
        strLastSeq = str(intLastSeq)

        self.txtSeq.setText(strLastSeq)

        self.txtTitle.setText("")
        self.txtDoActions.setText("")
        self.chkAlt.setChecked(False)
        self.chkCtrl.setChecked(False)
        self.chkShift.setChecked(False)
        self.txtShortCut.setText("")


    def f_get_item_data(self, tblWidget, row, col):
        rtn = ''
        item = tblWidget.item(row, col)
        if item != None:
            rtn = item.text()
        return rtn