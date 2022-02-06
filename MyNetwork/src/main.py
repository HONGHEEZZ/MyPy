
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QAxContainer import *


from src.MyHeader import *

import sys

'''
1. mid 참고
  .- https://www.tutorialspoint.com/pyqt/pyqt_multiple_document_interface.htm

2. riverbank pyqt5 class reference
  .- https://doc.bccnsoft.com/docs/PyQt5/class_reference.html
  .- https://doc.bccnsoft.com/docs/PyQt4/classes.html #qt4/qt5는 파이썬 2와 파이썬 3의 차이와 같다.
  
3. 아이콘
  .-  MyIconFinder(http://www.myiconfinder.com/)
  .- Flaticon(http://www.flaticon.com/)
  
  
4. TableWiget 사용법 매뉴얼
  .- https://doc.qt.io/archives/qtforpython-5.12/PySide2/QtWidgets/QTableWidget.html
  
5. 필요 QLibrary
pip install python-pptx
pip install cx-oracle
pip install pytube
pip install imapclient
easy_install pyzmail

6. 프로그레스바
self.progressBar_1.reset()
self.progressBar_1.setRange(0, cnt)
self.progressBar_1.setValue(row)


7. pyqt5 샘플site : https://python-catalin.blogspot.com/search/label/PyQt5

8. 공학자를 위한 PySide2
 .- https://wikidocs.net/35742
'''



# ui 파일 연결
form_class = uic.loadUiType("../ui/MyMainWindow.ui")[0]

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

        self.myCreateStatusBar() # 상태바
        self.statusbar = self.statusBar()

        self.myCreateDockWindow()

        # MDI 기본설정
        self.setWindowTitle("myThon")

        root = QFileInfo(__file__).absolutePath()
        self.setWindowIcon((QIcon(root + '/../img/main.png')))
        self.resize(1200, 800)

        # 추후 데이터베이스 파일이름을 가져오기 위한 변수
        self.DBLoad = ''

        self.OnHeader()

    def myCreateAction(self):
        root = QFileInfo(__file__).absolutePath()

        self.act_new_myheader = QAction(QIcon(root + '/../img/MyHeader.png'),
                                "&Header", self,
                                shortcut=QKeySequence.New,
                                statusTip="Header",
                                triggered=self.OnHeader)





        self.act_open = QAction(QIcon(root + '/../img/open.png'),
                                "&Open...", self,
                                shortcut=QKeySequence.Open,
                                statusTip="Open Case",
                                triggered=self.OnOpenCase)

        self.act_close = QAction(QIcon(root + '/../img/close.png'),
                                "&Close...", self,
                                shortcut=QKeySequence.Close,
                                statusTip="Close",
                                triggered=self.OnClose)




    def myCreateMenu(self):
        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenu.addAction(self.act_new_myheader)



        self.fileMenu.addAction(self.act_open)
        self.fileMenu.addAction(self.act_close)
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
        self.fileToolBar.addAction(self.act_new_myheader)

        self.fileToolBar.addAction(self.act_open)
        self.fileToolBar.addAction(self.act_close)

    def myCreateStatusBar(self):
        self.statusBar().showMessage("Ready") # 상태바에 Ready로 설정

    def OnHeader(self):

        # MyMainWindow.count = MyMainWindow.count + 1
        # sub = QMdiSubWindow()
        # sub.setWidget(QTextEdit())
        # sub.setWindowTitle("subwindow"+ str(MyMainWindow.count))
        # self.mdiArea.addSubWindow(sub)
        # sub.show()

        myform = CMyHeader(self)
        subWindow = self.mdiArea.addSubWindow(myform)
        subWindow.showMaximized()



    def OnOpenCase(self):
        if self.DBLoad == '':
            self.debuglog("> Error:: No database file!!!")
            #return


        print(mainWin)
        #self.openForm = test2.OpenFrom(parent=mainWin)
        self.openForm = test2.OpenFrom()
        self.openForm.updatesEnabled()
        self.openForm.setModal(True)
        self.openForm.show()
        self.debuglog(">Success:: File:test2->ClassWindow -> OpenCase exec")


    def OnClose(self):
        print("OnClose...")

    def debuglog(self, value):
        self.logInfo.addItem(value) # 로그 아이템 추가
        self.logInfo.updatesEnabled() # 추가한 item을 화면에 update
        self.logInfo.scrollToBottom() # 스크롤을 제일 밑으로 내림.

    # dockable Window
    def myCreateDockWindow(self):
        # Table View를 이용하여 기본정보를 표시하는 부분을 만들어준다.
        dock = QDockWidget("Information & File Path", self) # dock 이름설정

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

    msg = f"[Type] {exctype} \n [Value] {value} \n [Traceback] {traceback}"
    QMessageBox.critical(g_main, 'error', msg)
    # Call the normal Exception hook after
    sys._excepthook(g_main, exctype, value, traceback)
    # sys.exit(1)


if __name__ == "__main__":
    # Back up the reference to the exceptionhook
    sys._excepthook = sys.excepthook

    # Set the exception hook to our wrapping function
    sys.excepthook = my_exception_hook



    app = QApplication(sys.argv)

    # main 폼을 정의하는 부분
    mainWin = MyMainWindow()
    mainWin.show()

    # 이벤트루프
    # app.exec_()

    sys.exit(app.exec())