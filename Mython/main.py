from PyQt5.Qt import QApplication
from src.DocumentFormatConverter import *
from src.FileUploader import *
from src.MyYoutube import *
from src.MyRe import *
from src.MyWikiDocs import *
from src.MyMails import *
from src.MyEnglish import *

import sys

mainWin = None
g_app = QApplication(sys.argv)

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


8. pyQT 참고자료
 .- 초보자를 위한 Python GUI 프로그래밍 - PyQt5 : https://wikidocs.net/book/2944
 .- PyQt5 Tutorial - 파이썬으로 만드는 나만의 GUI 프로그램 : https://wikidocs.net/book/2165 
 .- 공학자를 위한 PySide2 : https://wikidocs.net/35742
 .- QT5 SITE : https://notstop.co.kr/479/
 .- 공학자를 위한 Python : https://wikidocs.net/book/1704
 
9. 파이썬 책 저장필요
 .- 파이썬 공식 매뉴얼 : https://docs.python.org/ko/3/library/
 .- 왕초보를 위한 Python: 쉽게 풀어 쓴 기초 문법과 실습
 .- 핵심만 간단히, Hello World! 파이썬 3
 
 10. 
 
시스템 트레이딩을 위한 데이터 사이언스 (파이썬 활용편)  --> 51번째 에러
---------------------------
error
---------------------------
*[Type] <class 'ValueError'> 
*[Value] not enough values to unpack (expected 4, got 3) 
*[Traceback] <traceback object at 0x0000021796AF4DC0>
---------------------------
OK   
---------------------------

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

        self.myCreateStatusBar() # 상태바
        self.statusbar = self.statusBar()

        #docking은 잠시 주석처리. English 끝나면 원복해야함. 2021.06.28
        #self.myCreateDockWindow()

        # MDI 기본설정
        self.setWindowTitle("myThon")

        root = QFileInfo(__file__).absolutePath()
        self.setWindowIcon((QIcon(root + './ico/shell32_dll_42_tree.ico')))
        self.resize(1200, 800)

        # 추후 데이터베이스 파일이름을 가져오기 위한 변수
        self.DBLoad = ''

        #self.OnFileConverter()
        #self.OnMyWikiDocs()
        self.OnMyEnglish()
        #self.OnMyMails()

    def myCreateAction(self):
        root = QFileInfo(__file__).absolutePath()

        self.act_new_fileConverter = QAction(QIcon(root + './img/fileConverter.png'),
                                "&File Converter", self,
                                shortcut=QKeySequence.New,
                                statusTip="File Converter",
                                triggered=self.OnFileConverter)

        self.act_new_fileUploader = QAction(QIcon(root + './img/fileUploadToDB.png'),
                                             "&File Converter", self,
                                             shortcut=QKeySequence.New,
                                             statusTip="File Uploader",
                                             triggered=self.OnFileUploader)

        self.act_new_myYoutube = QAction(QIcon(root + './img/youtube.png'),
                                            "&MyYoutube", self,
                                            shortcut=QKeySequence.New,
                                            statusTip="MyYoutube",
                                            triggered=self.OnMyYoutube)

        self.act_new_myRe = QAction(QIcon(root + './img/re.png'),
                                         "&Regular Expression", self,
                                         shortcut=QKeySequence.New,
                                         statusTip="Regular Expression",
                                         triggered=self.OnMyRe)

        self.act_new_myWickiDocs = QAction(QIcon(root + './img/wikiDocs.png'),
                                    "&WikiDocs", self,
                                    shortcut=QKeySequence.New,
                                    statusTip="Wiki Docs",
                                    triggered=self.OnMyWikiDocs)

        self.act_new_myEnglish = QAction(QIcon(root + './img/English.png'),
                                           "&English", self,
                                           shortcut=QKeySequence.New,
                                           statusTip="Engish",
                                           triggered=self.OnMyEnglish)

        self.act_new_myMails = QAction(QIcon(root + './img/mail.png'),
                                           "&MyMails", self,
                                           shortcut=QKeySequence.New,
                                           statusTip="MyMails",
                                           triggered=self.OnMyMails)



        self.act_open = QAction(QIcon(root + './img/open.png'),
                                "&Open...", self,
                                shortcut=QKeySequence.Open,
                                statusTip="Open Case",
                                triggered=self.OnOpenCase)

        self.act_close = QAction(QIcon(root + './img/close.png'),
                                "&Close...", self,
                                shortcut=QKeySequence.Close,
                                statusTip="Close",
                                triggered=self.OnClose)
# 차이점을 알 수 있을까? 이것은 169라인....
    def f_test(self):
        pass

    def myCreateMenu(self):
        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenu.addAction(self.act_new_fileConverter)
        self.fileMenu.addAction(self.act_new_fileUploader)

        self.fileMenu.addAction(self.act_new_myYoutube)
        self.fileMenu.addAction(self.act_new_myRe)
        self.fileMenu.addAction(self.act_new_myWickiDocs)
        self.fileMenu.addAction(self.act_new_myEnglish)
        self.fileMenu.addAction(self.act_new_myMails)


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
        self.fileToolBar.addAction(self.act_new_fileConverter)
        self.fileToolBar.addAction(self.act_new_fileUploader)
        self.fileToolBar.addAction(self.act_new_myYoutube)
        self.fileToolBar.addAction(self.act_new_myMails)
        self.fileToolBar.addAction(self.act_new_myRe)
        self.fileToolBar.addAction(self.act_new_myWickiDocs)
        self.fileToolBar.addAction(self.act_new_myEnglish)

        self.fileToolBar.addAction(self.act_open)
        self.fileToolBar.addAction(self.act_close)

    def myCreateStatusBar(self):
        self.statusBar().showMessage("Ready") # 상태바에 Ready로 설정

    def OnFileConverter(self):

        # MyMainWindow.count = MyMainWindow.count + 1
        # sub = QMdiSubWindow()
        # sub.setWidget(QTextEdit())
        # sub.setWindowTitle("subwindow"+ str(MyMainWindow.count))
        # self.mdiArea.addSubWindow(sub)
        # sub.show()

        myform = CDocumentFormatConverter(self)
        subWindow = self.mdiArea.addSubWindow(myform)
        subWindow.showMaximized()

    def OnFileUploader(self):

        myform = CFileUploader(self)
        subWindow = self.mdiArea.addSubWindow(myform)
        subWindow.showMaximized()

    def OnMyYoutube(self):

        myform = CMyYoutube(self)
        subWindow = self.mdiArea.addSubWindow(myform)
        subWindow.showMaximized()

    def OnMyRe(self):

        myform = CMyRe(self)
        subWindow = self.mdiArea.addSubWindow(myform)
        subWindow.showMaximized()

    def OnMyWikiDocs(self):

        myform = CMyWikiDocs(self)
        subWindow = self.mdiArea.addSubWindow(myform)
        subWindow.showMaximized()


    def OnMyEnglish(self):

        myform = CMyEnglish(self)
        subWindow = self.mdiArea.addSubWindow(myform)
        subWindow.showMaximized()

        self.resize(1100, 750)

    def OnMyMails(self):

        myform = CMyMails(self)
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



    #app = QApplication(sys.argv)

    # main 폼을 정의하는 부분
    mainWin = MyMainWindow()
    mainWin.show()

    # 이벤트루프
    # app.exec_()

    sys.exit(g_app.exec())