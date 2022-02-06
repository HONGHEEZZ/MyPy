
import sys
import os
import sqlite3

from PyQt5.QtWidgets import QApplication, QMessageBox, QWidget, QPushButton, \
                            QHBoxLayout, QAction, QMenu, QSystemTrayIcon, QCheckBox, \
                            QSpacerItem, QTextBrowser

from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt

from src.MyStickyDialog import *
from src.MyShortCutDlg import *
from src.MyKeyHook import *

import pyperclip # 클립보드



import sys
sys.path.append('../MyLib')
from MyLog import logger
from MyLog import LogStringHandler


g_main = None
g_screen_with = 0
g_screen_height = 0

g_width = 600 # 다이얼로그 너비
g_y_start = 200 # 다이얼로그 시작 y

g_x_margin = 100 # x 다이얼로그 오른쪽에서 여분
g_y_margin = 100 # y축 다이얼로그 하단 여분
g_new_pos = 7


strBtnBigStyleSheet = ("QPushButton {max-width:100px; min-height:20px;"
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

class MyApp (QWidget):
    def __init__ (self):
        super().__init__()

        self.setupUI()
        self.setupTrayIcon()

        g_main = self

        self.sticky_cnt_x =1
        self.sticky_cnt_y = 1

        # -
        # DB 파일 실행 경로를 소스파일 기준으로 변경한다.
        # -
        self.FILE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.BASE_DIR = os.path.join(self.FILE_DIR, ".")
        self.DB_FILE = os.path.join(self.BASE_DIR, "MyStickyNote.db")


        # DB 생성 (오토 커밋)
        self.conn = sqlite3.connect(self.DB_FILE)

        # self.setVisible (False)
        self.show()

        if self.f_open_sticky_note() == False:
            self.btnNew_clicked()

        self.move(g_screen_with - 690, 10)
        self.resize(600, 120)



    def closeEvent(self, event):
        if self.chkOnTray.isChecked():
            event.ignore()
            self.hide()
            self.tray_icon.showMessage(
            "MySticky Note",
            "MyStickyNote was minimized to Tray",
                    QSystemTrayIcon.Information,
                    1
            )

    def setupTrayIcon(self):
        # init QSytem Traylcon
        self.tray_icon = QSystemTrayIcon(self)
        icon = QIcon("./ico/shell32_dll_44_star.ico")
        show_action = QAction("Show", self)
        hide_action = QAction("Hide", self)
        quit_action = QAction("Quit", self)


        show_action.triggered.connect(self.show)
        hide_action.triggered.connect(self.hide)
        quit_action.triggered.connect(app.quit)
        tray_menu = QMenu()
        tray_menu.addAction(show_action)
        tray_menu.addAction(hide_action)
        tray_menu.addAction(quit_action)

        self.tray_icon.setIcon(icon)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def setupUI(self):

        self.setStyleSheet(("QWidget {background-color:#424242;border-radius:12px;}"))
        self.setFont(QFont("Consolas"))

        self.setStyleSheet(strBtnBigStyleSheet)

        self.setGeometry(800, 500, 200, 300)
        self.setWindowTitle('HStickyNote')
        self.setWindowIcon(QIcon('icon.png'))

        # 최상위 고정 버블
        self.btnOnTop = QPushButton("↑")
        self.btnOnTop.setShortcut("ctrl+t")

        # 기존 저장 열기버튼
        self.btnOpen = QPushButton("Saved")
        self.btnOpen.setShortcut("ctrl+o")

        # 새로 만들기 버튼
        self.btnNew = QPushButton("New")
        self.btnNew.setShortcut("ctrl+n")

        # 암호 1
        self.btnPwd1 = QPushButton("pwd1")
        self.btnPwd1.setShortcut("ctrl+1")

        # 암호 2.
        self.btnPwd2 = QPushButton("pwd2")
        self.btnPwd2.setShortcut("ctrl+2")

        # Hook시작
        self.btnHookStart = QPushButton("Hook시작")
        self.btnHookStart.setShortcut("ctrl+s")

        # Hook
        self.btnHookStop = QPushButton("Hook종료")
        self.btnHookStop.setShortcut("ctrl+t")
        self.btnHookStop.setEnabled(False)

        # 단축키 설정 대화상자
        self.btnDlgShortCut = QPushButton("단축키 관리")
        self.btnDlgShortCut.setShortcut("ctrl+s")


        # 이벤트 연결
        self.btnOnTop.clicked.connect(self.btnOnTop_clicked)
        self.btnOpen.clicked.connect(self.btnOpen_clicked)
        self.btnNew.clicked.connect(self.btnNew_clicked)
        self.btnPwd1.clicked.connect(self.btnPwd1_clicked)
        self.btnPwd2.clicked.connect(self.btnPwd2_clicked)
        self.btnHookStart.clicked.connect(self.btnHookStart_clicked)
        self.btnHookStop.clicked.connect(self.btnHookStop_clicked)
        self.btnDlgShortCut.clicked.connect(self.btnDlgShortCut_clicked)

        # hLayout에 버튼 담기
        h_layout1 = QHBoxLayout()
        h_layout1.addWidget(self.btnOnTop)
        h_layout1.addWidget(self.btnOpen)
        h_layout1.addWidget(self.btnNew)
        h_layout1.addWidget(self.btnPwd1)
        h_layout1.addWidget(self.btnPwd2)
        h_layout1.addWidget(self.btnHookStart)
        h_layout1.addWidget(self.btnHookStop)
        h_layout1.addWidget(self.btnDlgShortCut)
        h_layout1.addStretch()

        # hLayout에 여백 만들기
        h_layout1.setSpacing(5)
        h_layout2 = QHBoxLayout()
        self.chkOnTray = QCheckBox('Minimize to Tray')
        self.chkOnTray.setChecked(False)
        h_layout2.addWidget(self.chkOnTray)
        h_layout2.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding))

        h_layout3 = QHBoxLayout()
        self.txtBrowser = QTextBrowser()
        h_layout3.addWidget(self.txtBrowser)
        logger.addHandler(LogStringHandler(self.txtBrowser))



        v_layout = QVBoxLayout()
        v_layout.addItem(h_layout1)
        v_layout.addItem(h_layout2)
        v_layout.addItem(h_layout3)
        self.setLayout(v_layout)

    def btnHookStart_clicked(self):

        self.f_make_hook_setting()
        MyKeyHook.start()
        self.btnHookStart.setEnabled(False)
        self.btnHookStop.setEnabled(True)


    def f_make_hook_setting(self):
        #------------------------------------------------------------------------------
        # * DB 파일 실행 경로를 소스파일 기준으로 변경한다.
        #------------------------------------------------------------------------------
        self.FILE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.BASE_DIR = os.path.join(self.FILE_DIR, ".\\")
        self.DB_FILE = os.path.join(self.BASE_DIR, "MyShortCut.db")
        # DB 생성 (오토 커밋)
        self.conn = sqlite3.connect(self.DB_FILE)

        # 1. db에서 읽어온다.
        cursor = self.conn.cursor()

        sql = """
                SELECT
                    seq as seq,
                    Title,
                    ScDiv,
                    doAction,
                    Alt,
                    Ctrl,
                    Shift,
                    upper(ShortCut)
                FROM MyShortCut
                WHERE 1 = 1
                ORDER BY 1
        """
        cursor.execute(sql)
        rows = cursor.fetchall()
        if rows == None or len(rows) == 0:
            msg = "[MyShortCut.db] MyShortCut테이블에 자료 없음."
            # QMessageBox.information(self, '2', msg, QMessageBox. Yes)
            return

        colCount = len(rows[0])
        HOT_KEYS = {
            'MyFunc.print_hello': set([162, ord('5')])
            , 'MyFunc.copy_pwd_to_clipboard': set([162, 160, ord('V')])
            , 'MyFunc.uninstall Hook': set([162, 160, ord('9')])
        }

        KEY_LEFT_SHIFT = 160
        KEY_LEFT_CTRL = 162
        KEY_ALT = 18
        myHotkeys = []
        for row in rows:
            strSeq = row[0]
            strTitle = row[1]
            strScDiv = row[2]
            strdoAction = row[3]
            intAlt = row[4]
            intCtrl = row[5]

            intShift = row[6]
            strShortCut = row[7]
            keyUnion = set()

            if intShift: keyUnion.add(KEY_LEFT_SHIFT)
            if intCtrl: keyUnion.add(KEY_LEFT_CTRL)
            if intAlt: keyUnion.add(KEY_ALT)
            if strShortCut != "": keyUnion.add(ord(strShortCut))

            hk = [strSeq, strTitle, strScDiv, strdoAction, keyUnion]
            myHotkeys.append(hk)

        MyKeyHook.setHotkeys(myHotkeys)
        cursor.close()
        self.conn.close()

    def btnHookStop_clicked(self):
        MyKeyHook.stop()
        self.btnHookStart.setEnabled(True)
        self.btnHookStop.setEnabled(False)

    def btnDlgShortCut_clicked(self):
        dlg = MyShortCutDlg()
        dlg.exec_()

    def btnPwd1_clicked(self):
        pyperclip.copy("icis0624!!")

    def btnPwd2_clicked(self):
        pyperclip.copy("FRTB_IT3")

    def btnOnTop_clicked(self):
        blnNowOnTop = bool(self.windowFlags() & Qt.WindowStaysOnTopHint)


        # toggle
        blnNowOnTop= not blnNowOnTop

        strBtnText = "↑"
        if blnNowOnTop:
            strBtnText = "↓"

        self.setWindowFlag(Qt.WindowStaysOnTopHint, blnNowOnTop)
        self.btnOnTop.setText(strBtnText)

        self.show()

    def btnOpen_clicked(self):
        self.f_open_sticky_note()

    def btnNew_clicked(self):
        MyStickyDialog(self, "")

    # Sticky Note의 시작위치 지정
    def f_get_sticky_xy(self):

        # 시작위치 지정
        self.sdlg_x = g_screen_with - g_width - g_x_margin
        self.sdlg_x += self.sticky_cnt_x * g_new_pos
        self.sdlg_y = g_y_start

        self.sdlg_y += self.sticky_cnt_y * g_new_pos

        # 크기 지정
        self.sdlg_w = g_width
        self.sdlg_h = g_screen_height - g_y_start - g_y_margin

        if self.sticky_cnt_x * g_new_pos < g_x_margin:
            # 한번 호출될 때마다 x 증가시킴
            self.sticky_cnt_x += 3

            # y도 증가시킴...
            self.sticky_cnt_y += 3

        else:
            # 한 번 호출될 때마다 y 증가시킴
            self.sticky_cnt_y += 3

            # x는 초기화
            self.sticky_cnt_x = 3

        # cnt_y 초기화
        if self.sdlg_y > g_screen_height:
            self.sticky_cnt_y += 3

        return (self.sdlg_x,
                self.sdlg_y,
                self.sdlg_w,
                self.sdlg_h)

    # db 에서 저장되어 있는 노트 가져와서 Sticky Dialog 열기
    def f_open_sticky_note(self):

        # 1. db에서 읽어 온다.
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
                ORDER BY seq"""

        cursor.execute(sql)
        rows = cursor.fetchall()

        #
        # 한건도 없는 경우 빈 StickyNote 를 생성 후 종료
        #
        if rows == None or len(rows) == 0:

            #QMessageBox.warning(self, "불러오기", "저장된 데이터가 없습니다.", QMessageBox. Yes)
            return False

        # -
        # * 저장된 데이터가 있는 경우 저장된 모든 것을 열어준다.
        # -
        for row in rows:
            seq = str(row[0])

            MyStickyDialog(self, seq)

        return True

def my_exception_hook(exctype, value, traceback):
    # Print the error and traceback
    print(exctype, value, traceback)

    msg = f"[Type] {exctype} \n [Value] {value} \n [Traceback] {traceback}"
    QMessageBox.critical(g_main, 'error', msg)
    # Call the normal Exception hook after
    sys._excepthook(g_main, exctype, value, traceback)
    # sys.exit(1)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    screen_rect = app.desktop().screenGeometry()
    g_screen_with = screen_rect.width()
    g_screen_height = screen_rect.height()

    ex = MyApp()

    sys.exit(app.exec_())

