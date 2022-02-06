import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QDialog, QWidget
from PyQt5.QtWidgets import QLabel, QLineEdit, QPushButton, QTextEdit
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout,QSpacerItem, QSizePolicy, QSizeGrip

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt, QPoint

import os
import time
import datetime
import sqlite3
import pyperclip

# 클립보드
from src.MyCustomTitleBar import *

# 큰 버튼

strBtnBigStyleSheet = ("QPushButton {max-width:50px; min-height:20px;"
            "color:#4fc3f7;"
            "background-color:#424242;"
            #"border:2px solid #4fc3f7;"
            "border-radius:8px;"
            "font-size:12px;"
            "font-weight:bold;}"
            +
            "QPushButton:hover {color:#212121;"
            "background-color:#4fc3f7;}"
            +
            "QPushButton:pressed {color:white;"
            "background-color:#212121;"
            "border-color:white;}"
)

# 작은 버튼

strBtnSmallStyleSheet = ("QPushButton {max-width:20px; min-height:20px;"
            "color:#4fc3f7;"
            "background-color:#424242;"
            #"border:2px solid #4fc3f7;"
            "border-radius:8px;"
            "font-size:12px;"
            "font-weight:bold;}"
            +
            "QPushButton:hover {color:#212121;"
            "background-color:#4fc3f7;}"
            +
            "QPushButton:pressed {color:white;"
            "background-color:#212121;"
            "border-color:white;}"
)


class MyStickyDialog (QDialog):

    def __init__(self, parent, seq = ""):

        QDialog.__init__(self, parent)
        self.parent = parent
        self.seq = seq

        # -
        # DB 파일 실행 경로를 소스파일 기준으로 변경한다.
        # -
        self.FILE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.BASE_DIR = os.path.join(self.FILE_DIR, "..\\")
        self.DB_FILE = os.path.join(self.BASE_DIR, "MyStickyNote.db")

        # DB 생성 (오토 커밋)
        self.conn = sqlite3.connect (self. DB_FILE)

        self.gap = 20
        self.start_y = 100
        self.width_y = 600

        # super(). init ()

        self.setModal (0)
        self.setWindowFlag (Qt. FramelessWindowHint)
        self.setWindowFlag (Qt.WindowStaysOnTopHint)
        self.setWindowFlag (Qt.WindowStaysOnTopHint, False)

        # 원도우 크기 조정 가능하게 설정...
        self.gripSize = 16
        self.grips = []
        for i in range (4):
            grip = QSizeGrip(self)
            grip.resize(self.gripSize, self.gripSize)
            self.grips.append(grip)

        self.setupUI ()

        # key값을 seqLabel에 셋팅
        self.lblSeq.setText(seq)

        # 저장된 값을 읽어 화면에 보여준다. seq가 있을때만 ...
        if seq:
            self.f_load_sticky_note()

        self.show()

    def setupUI (self):
        self.setStyleSheet (strBtnBigStyleSheet)
        self.setGeometry(1100, 200, 300, 100)
        self.setWindowTitle("Sticky Note")
        self.setWindowIcon (QIcon('icon.png'))

        self.TextEdit1 = QTextEdit()
        self.TextEdit1.setPlaceholderText ("메모를 작성하세요...")

        self.btnOnTop = QPushButton("↑")

        self.btnNew = QPushButton("+")
        self.btnNew.setShortcut("ctrl+n")

        self.btnOnTop.setStyleSheet(strBtnSmallStyleSheet)
        self.btnNew.setStyleSheet(strBtnSmallStyleSheet)

        #
        # 최하단 일련번호와 저장버튼
        #
        self.btnSave = QPushButton("저장")
        self.btnSave.setShortcut ("ctrl+s")

        self.btnDelete = QPushButton("삭제")
        self.btnDelete.setShortcut("ctrl+d")

        self.lblSeq = QLabel("")
        hlay_2 = QHBoxLayout()

        # hlay_2.addStretch (1)

        hlay_2.addWidget(self.btnSave)
        hlay_2.addWidget(self.btnDelete)
        hlay_2.addWidget(self.lblSeq)
        hlay_2.addStretch(50)

        #
        # VboxLayout 메인 테스트 박스 추가
        #

        vlay_2 = QVBoxLayout()
        vlay_2.setContentsMargins(0, 0, 0, 0)
        vlay_2.addWidget(self.TextEdit1)
        vlay_2.addLayout(hlay_2)

        # self.set Layout (layout)
        self.btnOnTop.clicked.connect(self.btnOnTopClicked)
        self.btnNew.clicked.connect(self.btnNewClicked)
        self.btnSave.clicked.connect(self.btnSaveClicked)
        self.btnDelete.clicked.connect(self.btnDeleteClicked)

        #
        # 커스텀 타이틀 바
        #
        custom_titlebar = MyCustomTitleBar(self)

        hlay_1 = QHBoxLayout()

        hlay_1.setContentsMargins(0, 0, 0, 0)
        hlay_1.addWidget(self.btnOnTop) # 항상 위
        hlay_1.addWidget(self.btnNew)  # 새로 추가
        hlay_1.addWidget(custom_titlebar)

        # 페이지 Main Vlayout....
        vlay_1 = QVBoxLayout(self)
        vlay_1.addLayout(hlay_1) # 커스텀 타이를바
        vlay_1.addLayout(vlay_2) # 메인 텍스트 박스


        x, y, w, h = self.parent.f_get_sticky_xy()
        self.move(x, y)
        self.resize(w, h)

    # 윈도우 크기 조절 가능 그립
    def resizeEvent(self, event):

        rect = self.rect()
        # top left grip doesnt need to be moved.
        # top right
        self.grips[1].move(rect.right() - self.gripSize, 0)

        # bottom right
        self.grips[2].move(rect.right() - self.gripSize, rect.bottom() - self.gripSize)

        # bottom left
        self.grips[3].move(0, rect.bottom() - self.gripSize)

    # 저장 버튼 클릭
    def btnSaveClicked(self):
        self.f_save()


    # 삭제
    def btnDeleteClicked(self):

        seq = self.lblSeq.text()

        # 저장여부 확인.
        if seq == "":

            QMessageBox.question(self, "확인", "저장된 메모가 아닙니다. 삭제할 수 없습니다.")
            return

        # 삭제 확인
        ret = QMessageBox.question(self, "확인", "현재 메모를 삭제하시겠습니까?")
        if ret == QMessageBox.No:
            return

        if self.f_delete():
            self.close()

    # seq
    def f_get_seq(self):

        # 1. db에서 읽어온다.
        cursor = self.conn.cursor()

        sql = f"""
                select ifnull(max(seq), 0) + 1 as next_seq
                from MyStickyNote
                """
        cursor.execute(sql)
        row = cursor.fetchone()

        next_seq = row[0]

        cursor.close()
        return next_seq

    # 저장
    def f_save(self):
        seq = self.lblSeq.text()
        strTitle = ""
        strContents = self.TextEdit1.toPlainText()

        # 1. db에서 읽어온다.
        cursor = self.conn.cursor()
        if seq:
            sql = f"""
                update MystickyNote set
                
                    title = ?,
                    contents = ?,
                    up_dt = (datetime('now', 'localtime'))
                where seq = ?
            """
            cursor.execute(sql, (strTitle, strContents, seq))

        else:
            seq = self.f_get_seq()

            sql = """
            insert into MystickyNote( seq, title, contents )
            values (?, ?, ?)
            """

            cursor.execute(sql, (seq, strTitle,strContents))

        if cursor.rowcount != 1:
            QMessageBox.warning(self, '오류', f"1건만 입력 / 수정되어야 하는데 [{cursor. rowcount})]건이 영향받음. 오류 확인 할 것", QMessageBox. Yes)

        cursor.close()

        self.conn.commit()
        self.lblSeq.setText(str(seq))

    #삭제
    def f_delete (self):
        seq = self.lblSeq.text()

        if seq == "":
            QMessageBox. question(self, '확인', "저장된 메모가 아닙니다. 삭제할 수 없습니다.")
            return False


        # 1. db에서 읽어온다.
        cursor= self.conn.cursor()

        sql = """
                delete from MyStickyNote
                where seq = ?
                """

        cursor.execute(sql, (seq,))

        if cursor.rowcount != 1:
            QMessageBox.warning(self, '오류', f"1건만 입력 / 수정되어야 하는데 [{cursor.rowcount})]건이 영향받음. 오류 확인 할 것", QMessageBox.Yes)

        cursor.close()
        self.conn.commit()

        return True

    #저장되어 있는 Sticky Note 불러오기
    def f_load_sticky_note (self):
        title, contents, ins_dt, up_dt = self.f_query(self.seq)
        self.TextEdit1.setPlainText (contents)

    # db에서 내용 읽어오기
    def f_query(self, seq):

        # 1. db에서 읽어온다.
        cursor = self.conn.cursor()

        sql = """
            SELECT
                seq,
                title,
                contents,
                etc,
                ins_dt,
                up_dt
    
            FROM MyStickyNote
            WHERE seq = ?
        """

        cursor.execute(sql, (seq,))
        row = cursor.fetchone()



        if row == None or len(row) == 0:
            return

        cursor.close()

        title = row[1]
        contents = row[2]
        ins_dt = row[4]
        up_dt = row[5]

        return title, contents, ins_dt, up_dt

    # 새 메모 열기
    def btnNewClicked(self):
        self.parent.btnNew_clicked()

    # 항상 위에 있기 버튼 클릭
    def btnOnTopClicked(self):
        blnNowOnTop = bool(self.windowFlags() & Qt.WindowStaysOnTopHint)

        # toggle
        blnNowOnTop = not blnNowOnTop

        strBtnText = "↑"
        if blnNowOnTop:
            strBtnText = "↓"

        self.setWindowFlag(Qt.WindowStaysOnTopHint, blnNowOnTop)
        self.btnOnTop.setText(strBtnText)
        self.show()
