import sys, os

from PyQt5.Qt import QApplication

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtCore import QFileInfo

from PyQt5 import uic

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QAction, qApp, QApplication, QDesktopWidget
from PyQt5.QtWidgets import QMenu, QPlainTextEdit, QSizePolicy, QMdiArea, QMessageBox, QDockWidget
from PyQt5.QtWidgets import QTableView, QTreeView, QListWidget

from PyQt5.QtGui import QIcon, QFont


from src.mainVirus import *

mainWin = None
g_app = QApplication(sys.argv)

'''


'''

# ui 파일 연결
form_class = uic.loadUiType("./ui/MyMainWindow.ui")[0]

g_main = None


class MyMainWindow(QMainWindow, form_class):
    count = 0

    def __init__(self):
        super(MyMainWindow, self).__init__()
        self.setupUi(self)

        g_main = self

        # Window 속성을 MDI로 만든다.
        self.mdiArea = QMdiArea()

        # 수평/수직 스크롤 사용
        self.mdiArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.mdiArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # window 중앙에 위치시킴
        self.setCentralWidget(self.mdiArea)

        # 초기화()
        self.myCreateAction()
        self.myCreateMenu()
        self.myCreateToolBar()

        self.myCreateStatusBar()  # 상태바
        self.statusbar = self.statusBar()

        # docking은 잠시 주석처리. English 끝나면 원복해야함. 2021.06.28
        # self.myCreateDockWindow()

        # MDI 기본설정
        self.setWindowTitle("MyAntiVirus")

        root = QFileInfo(__file__).absolutePath()
        self.setWindowIcon((QIcon(root + './img/main.png')))
        self.resize(300, 200)

        # 추후 데이터베이스 파일이름을 가져오기 위한 변수
        self.DBLoad = ''

        # self.OnFileConverter()
        # self.OnMyWikiDocs()
        # self.OnMyEnglish()
        # self.OnMyMails()

    def myCreateAction(self):
        root = QFileInfo(__file__).absolutePath()

    # 차이점을 알 수 있을까? 이것은 169라인....
    def f_test(self):
        pass

    def myCreateMenu(self):
        self.fileMenu = self.menuBar().addMenu("&File")

        self.fileMenu.addSeparator()

        self.windowMenu = self.menuBar().addMenu("&Window")
        self.windowMenu.addAction("Cascade")
        self.windowMenu.addAction("Tiled")
        self.windowMenu.triggered[QAction].connect(self.windowMenuAction)

    def windowMenuAction(self, q):
        if q.text() == "Cascade":
            print("Cascade")
            self.mdiArea.cascadeSubWindows()
        elif q.text() == "Tiled":
            print("Tiled")
            self.mdiArea.tileSubWindows()

    def myCreateToolBar(self):
        self.fileToolBar = self.addToolBar("File")

    def myCreateStatusBar(self):
        self.statusBar().showMessage("Ready")  # 상태바에 Ready로 설정

    def OnClose(self):
        print("OnClose...")

    def debuglog(self, value):
        self.logInfo.addItem(value)  # 로그 아이템 추가
        self.logInfo.updatesEnabled()  # 추가한 item을 화면에 update
        self.logInfo.scrollToBottom()  # 스크롤을 제일 밑으로 내림.

    # dockable Window
    def myCreateDockWindow(self):
        # Table View를 이용하여 기본정보를 표시하는 부분을 만들어준다.
        dock = QDockWidget("Information & File Path", self)  # dock 이름설정

        # dock 위치 지정
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        # 설정된 값을 fileInfoTable에 넣어준다.
        self.myFileInfoTable = QTableView(dock)
        self.myTableFont = QFont("Verdana", 8)
        self.myFileInfoTable.setFont(self.myTableFont)
        self.myFileInfoTable.setAlternatingRowColors(True)
        self.myFileInfoTable.setShowGrid(True)

        dock.setWidget(self.myFileInfoTable)

        self.addDockWidget(Qt.LeftDockWidgetArea, dock)

        # ------------------------------------------------------------------------------
        # Row Table View
        # ------------------------------------------------------------------------------
        dock = QDockWidget("Row Information", self)
        dock.setAllowedAreas(Qt.RightDockWidgetArea)
        self.rowInfoTable = QTableView(dock)

        # table 정의 부분
        self.rowInfoTable.setFont(self.myTableFont)
        self.rowInfoTable.setAlternatingRowColors(True)
        self.rowInfoTable.setShowGrid(True)

        dock.setWidget(self.rowInfoTable)

        self.addDockWidget(Qt.RightDockWidgetArea, dock)

        # ------------------------------------------------------------------------------
        # Tree View를 이용하여 엑셀 원본 및 변환 파일등을 계층으로 표시한다.
        # ------------------------------------------------------------------------------
        dock = QDockWidget("Case Structure", self)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea |
                             Qt.RightDockWidgetArea)
        self.treefolder = QTreeView(dock)
        self.treefolder.setAlternatingRowColors(True)
        self.treefolder.setContextMenuPolicy(Qt.CustomContextMenu)
        self.treefolder.customContextMenuRequested.connect(self.showCustomContextMenu)
        self.treefolder.setSortingEnabled(False)

        dock.setWidget(self.treefolder)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock)

        # ------------------------------------------------------------------------------
        # List View를 이용하여 디버그 창을 만들어 준다.
        # ------------------------------------------------------------------------------
        dock = QDockWidget("Debug & Processing Log...", self)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea |
                             Qt.RightDockWidgetArea |
                             Qt.BottomDockWidgetArea)
        self.logInfo = QListWidget(dock)
        dock.setWidget(self.logInfo)
        self.addDockWidget(Qt.BottomDockWidgetArea, dock)

    def showCustomContextMenu(self, pos):
        index = self.treefolder.indexAt(pos)


def my_exception_hook(exctype, value, traceback):
    # Print the error and traceback
    print(exctype, value, traceback)

    msg = f"*[Type] {exctype} \n*[Value] {value} \n*[Traceback] {traceback}"
    QMessageBox.critical(g_main, 'error', msg)
    # Call the normal Exception hook after
    sys._excepthook(g_main, exctype, value, traceback)
    # sys.exit(1)


if __name__ == "__main__":
    # Back up the reference to the exceptionhook
    sys._excepthook = sys.excepthook

    # Set the exception hook to our wrapping function
    sys.excepthook = my_exception_hook

    # app = QApplication(sys.argv)

    # ------------------------------------------------------------------------------
    # * 여기서 main() 함수를 호출한다.
    # ------------------------------------------------------------------------------
    mainVirus()

    # main 폼을 정의하는 부분
    mainWin = MyMainWindow()
    mainWin.show()

    # 이벤트루프
    # app.exec_()

    sys.exit(g_app.exec())
