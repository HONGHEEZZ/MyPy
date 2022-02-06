
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
#from PyQt5.QAxContainer import *


from src.MyExplorer import *
from src.MyIniFile import *




import sys

'''
1. mdi 참고
  .- https://www.tutorialspoint.com/pyqt/pyqt_multiple_document_interface.htm

2. riverbank pyqt5 class reference
  .- https://doc.bccnsoft.com/docs/PyQt5/class_reference.html
  .- https://doc.bccnsoft.com/docs/PyQt4/classes.html #qt4/qt5는 파이썬 2와 파이썬 3의 차이와 같다.
  
3. 아이콘
  .-  MyIconFinder(http://www.myiconfinder.com/)
  .- Flaticon(http://www.flaticon.com/)
  .- https://icon-icons.com/ko/
  
  
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
 
9. 추가 스크랩
 .- 핵심만 간단히, Hello World! 파이썬 3    2021. 07.07
 
 lxml, xmltodict
'''



# ui 파일 연결
form_class = uic.loadUiType("ui/MyMainWindow.ui")[0]

g_main = None

class MyMainWindow(QMainWindow, form_class):
    count = 0

    def closeEvent(self, event):


        print('************************* MyMainWindow closeEvent ******************')
        self.myIniFileMgr.save(self)



    def onNew(self, strTitle = ''):

        myform = CMyExplorer(self)
        #QMdiSubWindow
        mdiSubWindow = self.mdiArea.addSubWindow(myform)
        if strTitle:
            mdiSubWindow.setWindowTitle(strTitle)
        mdiSubWindow.showMaximized()

        # 오른쪽 마우스 클릭
        # 컨텍스트 메뉴
        mdiSubWindow.setContextMenuPolicy(Qt.CustomContextMenu)
        mdiSubWindow.customContextMenuRequested.connect(self.on_contextMenu)


    def on_contextMenu(self, position):
        print('**********main... on_contextMenu')


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

        # mid 뷰 코드 선택...
        self.mdiArea.setViewMode(QMdiArea.TabbedView)


        # 초기화()
        self.myCreateAction()
        self.myCreateMenu()
        self.myCreateToolBar()

        self.myCreateStatusBar() # 상태바
        self.statusbar = self.statusBar()

        #self.myCreateDockWindow()

        # MDI 기본설정
        self.setWindowTitle("myExplorer")

        root = QFileInfo(__file__).absolutePath()
        self.setWindowIcon((QIcon(root + './img/main.png')))
        self.resize(1200, 800)

        # 추후 데이터베이스 파일이름을 가져오기 위한 변수
        self.DBLoad = ''


        #------------------------------------------------------------------------------
        #* ini 파일 처리
        # ------------------------------------------------------------------------------
        self.config_file_name = 'MyExplorer.ini'
        self.myIniFileMgr = CMyIniFile(self, self.config_file_name)

        if 0 == self.myIniFileMgr.load_mdi(self):
            # init 파일에 없을때 처리...
            self.onNew('Title_hanhonghee2...')

        self.myIniFileMgr.load_position(self)

    def myCreateAction(self):
        root = QFileInfo(__file__).absolutePath()

        self.act_new_MyExplorer = QAction(QIcon(root + './img/explorer.png'),
                                          "&Explorer", self,
                                          shortcut=QKeySequence.New,
                                          statusTip="Explorer",
                                          triggered=self.onNew)

        self.act_open = QAction(QIcon(root + './img/openfile.png'),
                                "&Open...", self,
                                shortcut=QKeySequence.Open,
                                statusTip="Open Case",
                                triggered=self.onOpenCase)

        self.act_close = QAction(QIcon(root + './img/close.png'),
                                 "&Close...", self,
                                 shortcut=QKeySequence.Close,
                                 statusTip="Close",
                                 triggered=self.onClose)

        self.act_edit_copy = QAction(QIcon(root + './img/file_copy.png'),
                                     "&Copy", self,
                                     shortcut=QKeySequence(Qt.CTRL + Qt.Key_C),
                                     statusTip="FileCopy",
                                     triggered=self.onFileCopy)

        self.act_edit_copy_filename_only = QAction(QIcon(root + './img/file_copy.png'),
                                                   "Copy &FileNameOnly", self,
                                                   shortcut=QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_C),
                                                   statusTip="FileCopyFileNameOnly",
                                                   triggered=self.onFileCopyFileNameOnly)

        self.act_edit_paste = QAction(QIcon(root + './img/file_paste.png'),
                                      "&Paste", self,
                                      shortcut=QKeySequence(Qt.CTRL + Qt.Key_V),
                                      statusTip="FilePaste",
                                      triggered=self.onFilePaste)

        self.act_edit_delete = QAction(QIcon(root + './img/delete.png'),
                                       "&Delete", self,
                                       shortcut=QKeySequence.Delete,
                                       statusTip="FileDelete",
                                       triggered=self.onEditDelete)

        self.act_edit_rename_file = QAction(QIcon(root + './img/rename_file.png'),
                                            "&Rename File", self,
                                            shortcut="F2",
                                            statusTip="rename file",
                                            triggered=self.onEditRenameFile)

        self.act_edit_rename_tab = QAction(QIcon(root + './img/rename_tab.png'),
                                           "&Rename Tab", self,
                                           # shortcut="F2",
                                           statusTip="rename tab",
                                           triggered=self.onEditRenameTab)

        self.act_edit_rename_mdi = QAction(QIcon(root + './img/rename_mdi.png'),
                                           "&Rename MDI", self,
                                           # shortcut="F2",
                                           statusTip="rename MDI",
                                           triggered=self.onEditRenameMdi)

        self.act_file_info = QAction(QIcon(root + './img/info.png'),
                                     "FileInfo", self,
                                     shortcut="F10",
                                     statusTip="FileInfo",
                                     triggered=self.onFileInfo)



    def myCreateMenu(self):

        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenu.addAction(self.act_new_MyExplorer)
        self.fileMenu.addSeparator()

        self.fileMenu.addAction(self.act_open)
        self.fileMenu.addAction(self.act_close)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.act_file_info)
        self.fileMenu.addSeparator()

        self.editMenu = self.menuBar().addMenu("&Edit")
        self.editMenu.addAction(self.act_edit_copy)
        self.editMenu.addAction(self.act_edit_paste)
        self.editMenu.addAction(self.act_edit_delete)

        self.editMenu.addSeparator()
        self.editMenu.addAction(self.act_edit_copy_filename_only)


        self.editMenu.addSeparator()
        self.editMenu.addAction(self.act_edit_rename_file)
        self.editMenu.addAction(self.act_edit_rename_tab)
        self.editMenu.addAction(self.act_edit_rename_mdi)
        self.editMenu.addSeparator()

        self.windowMenu = self.menuBar().addMenu("&Window")
        self.windowMenu.addAction("Cascade")
        self.windowMenu.addAction("Tiled")
        self.windowMenu.triggered[QAction].connect(self.windowMenuAction)

    def myCreateToolBar(self):
        self.fileToolBar = self.addToolBar("File")
        self.fileToolBar.addAction(self.act_new_MyExplorer)

        self.fileToolBar.addAction(self.act_open)
        self.fileToolBar.addAction(self.act_close)

        self.editToolBar = self.addToolBar("Edit")
        self.editToolBar.addAction(self.act_edit_copy)
        self.editToolBar.addAction(self.act_edit_paste)

        self.editToolBar.addAction(self.act_edit_delete)

        self.editToolBar.addSeparator()
        self.editToolBar.addAction(self.act_edit_rename_file)
        self.editToolBar.addAction(self.act_edit_rename_tab)
        self.editToolBar.addAction(self.act_edit_rename_mdi)

        self.infoToolBar = self.addToolBar("Info")
        self.infoToolBar.addAction(self.act_file_info)


    def windowMenuAction(self, q):
        if q.text() == "Cascade":
            print("Cascade")
            self.mdiArea.cascadeSubWindows()
        elif q.text() == "Tiled":
            print("Tiled")
            self.mdiArea.tileSubWindows()



    def myCreateStatusBar(self):
        self.statusBar().showMessage("Ready") # 상태바에 Ready로 설정


    def getActiveSubWindow(self):
        # self.mdiArea.addSubWindow(self.subwindow)
        # print("there is a subwindow activated")
        # self.mdiArea.activeSubWindow()
        # self.subwindow.show()
        activeSubWindow = self.mdiArea.activeSubWindow()

        if activeSubWindow == None:
            mdiSubWindows = self.mdiArea.subWindowList()
            if len(mdiSubWindows) == 0:
                return None
            else:
                activeSubWindow = mdiSubWindows[0]

        print("this is subwindow 1 [" + str(activeSubWindow.widget().objectName()), "]")
        return activeSubWindow

    def getActiveSubWindowIndex(self):
        activeSubWindow = self.getActiveSubWindow()

        mdiSubWindows = self.mdiArea.subWindowList()

        cnt = len(mdiSubWindows)
        index = 0
        for i in range(cnt):
            if activeSubWindow == mdiSubWindows[i]:
                index = i
                break

        return index

    def setActiveSubWindowByIndex(self, index):


        mdiSubWindows = self.mdiArea.subWindowList()

        find_index = index
        if index==0:
            find_index = len(mdiSubWindows)-1

        subWindow = mdiSubWindows[find_index]

        if index == 0:
            #index ==0일때는 제대로 setActiveSubWindow 버그발생
            # 마지막 인덱스 +1로 처리해서 해결함. 2021.07.02
            self.mdiArea.setActiveSubWindow(subWindow)
            self.mdiArea.activateNextSubWindow()

        else:
            self.mdiArea.setActiveSubWindow(subWindow)


    def onEditDelete(self):
        activeSubWindow = self.getActiveSubWindow()
        myform = activeSubWindow.widget()
        myform.onDelete()

    def onEditRenameFile(self):
        activeSubWindow = self.getActiveSubWindow()
        myform = activeSubWindow.widget()
        myform.onRenameFile()

    def onEditRenameTab(self):
        activeSubWindow = self.getActiveSubWindow()
        myform = activeSubWindow.widget()
        myform.onRenameTab()

    def onEditRenameMdi(self):
        activeSubWindow = self.getActiveSubWindow()

        strMdiTabText = activeSubWindow.windowTitle()

        text, res = QInputDialog.getText(self, "MDI 탭 이름 바꾸기", "바꿀 MDI 탭 이름을 입력하세요.", QLineEdit.Normal, strMdiTabText)
        if res:
            activeSubWindow.setWindowTitle(text)

    def onFileCopy(self):
        print("************* OnFileCopy ***************")
        activeSubWindow = self.getActiveSubWindow()
        myform = activeSubWindow.widget()
        myform.onFileCopy()


    def onFileCopyFileNameOnly(self):
        print("************* onFileCopyFileNameOnly ***************")
        activeSubWindow = self.getActiveSubWindow()
        myform = activeSubWindow.widget()
        myform.onFileCopyFileNameOnly()

    def onFilePaste(self):
        print("************* OnFileCopy ***************")
        activeSubWindow = self.getActiveSubWindow()
        myform = activeSubWindow.widget()
        myform.onFilePaste()


    def onFileInfo(self):
        print("************* OnFileInfo ***************")
        activeSubWindow = self.getActiveSubWindow()
        myform = activeSubWindow.widget()
        myform.onFileInfo()

    def onOpenCase(self):
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


    def onClose(self):
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
    #여기서 내 Library path를 추가한다.
    sys.path.append('../MyLib')

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