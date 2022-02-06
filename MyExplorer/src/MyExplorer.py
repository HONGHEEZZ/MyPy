import PyQt5.QtWidgets as QtWidgets

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic

import os
import shutil
from socket import *
import time

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot


import win32api


import os
import glob

import shutil

from src.MyCursor import *
from src.MyTreeView import *
from src.MyTableView import *
from src.MyDoWithFiles import *
from src.MyFindFiles import *
from src.MyPhoto import *
from src.MyPhoto2 import *
from src.MyFileInfo import *
from src.MyProject_DayWork import *

#여기서 내 Library path를 추가한다.
sys.path.append('../MyLib')
import MyLibDlg_InputDialog
'''

* 파이썬 ui 참고 자료 - wikidoc
- PyQt5 Tutorial - 파이썬으로 만드는 나만의 GUI 프로그램
- 초보자를 위한 Python GUI 프로그래밍 - PyQt5 <---------------TableView 좋음...  test6.py
- python_ Cheat Sheet
- 시그널/슬롯 : https://wikidocs.net/21876 비트코인 자동 매매...

'''

# 책 https://wikidocs.net/book/1
# 책 - 챕터 https://wikidocs.net/2


# do lengthy process
QApplication.restoreOverrideCursor()

my_dlg = uic.loadUiType("ui/MyExplorer.ui")[0]


class CMyExplorer(QDialog, my_dlg):
    def __init__(self, parent=None, config=None):
        print("parent:", parent)
        super().__init__(parent)
        self.setupUi(self)
        # loadUi("test2",self)

        self.config = config

        self.initUI()
        self.url_back = []

    # 2021.03.19 현재 소멸자 호출 안됨...
    def __del__(self):
        pass
        # for i in range(0, self.cboImage.count()):
        #     if self.dialog[i]:
        #         self.dialog[i].close()

    def f_load_config(self):
        # ------------------------------------------------------------------------------
        # * 탭을 만든다.
        # ------------------------------------------------------------------------------
        config = self.config


        if config == None:
            tab1 = QWidget()
            tab2 = QWidget()
            tab3 = QWidget()

            tab1.my_cur_dir = r"z:\02.hanhonghee\01.MyPg\55.MyPy\MyExplorer\src"
            tab2.my_cur_dir = r"r:\02.hanhonghee"
            tab3.my_cur_dir = r"z:\client32"

            self.txtUrl.setText(tab1.my_cur_dir)

            self.tabs = QTabWidget()
            self.tabs.setMovable(True) #탭 이동 가능 설정
            self.tabs.addTab(tab1, 'Tab1')
            self.tabs.addTab(tab2, 'Tab2')
            self.tabs.addTab(tab3, 'Tab3')

            return

        str_tab_count = config['tab_count']


        tab_count = int(str_tab_count)
        self.tabs = QTabWidget()
        self.tabs.setMovable(True)  # 탭 이동 가능 설정
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)

        self.tabs.tabCloseRequested.connect(self.removeTab)

        for index in range(tab_count):
            tab_new = QWidget()

            tab_name_key = f"tab_name_{index}"  # 탭이름
            dir_name_key = f"directory_{index}"  # directory

            tab_name_value = config[tab_name_key]
            dir_name_value = config[dir_name_key]

            tab_new.my_cur_dir = dir_name_value

            
            self.tabs.addTab(tab_new, tab_name_value)

        if self.tabs.count() > 0:
            # txtUrl에 첫번째 탭의 url을 지정
            tab = self.tabs.widget(0)
            self.txtUrl.setText(tab.my_cur_dir)

    #------------------------------------------------------------------------------
    #* 탭 옆에 있는 x 버튼...
    # ------------------------------------------------------------------------------
    def removeTab(self, index):
        widget = self.tabs.widget(index)
        if widget is not None:
            widget.deleteLater()
        self.tabs.removeTab(index)


    def initUI(self):
        self.setWindowTitle('MyExplorer')
        self.setMinimumSize(200, 200)

        # grid = QGridLayout()
        grid = self.gridLayout
        # grid.setSpacing(12)
        self.setLayout(grid)




        #------------------------------------------------------------------------------
        #* url 텍스트 박스
        # ------------------------------------------------------------------------------
        # addWidget (self, QWidget, row, column, rowSpan, columnSpan, Qt.Alignment alignment = 0)
        self.txtUrl = QLineEdit()
        grid.addWidget(self.txtUrl, 1, 1, 1, 10)
        self.txtUrl.returnPressed.connect(self.txtUrl_returnPressed)

        # ------------------------------------------------------------------------------
        # * config 파일 로드
        # ------------------------------------------------------------------------------
        self.f_load_config()


        self.btnBack = QPushButton('Back')
        grid.addWidget(self.btnBack, 1, 0, 1, 1)

        #go button
        self.btnGo = QPushButton('Go')
        grid.addWidget(self.btnGo, 1, 11, 1, 1)

        # Short cut 지정
        QShortcut(Qt.Key_F5, self.btnGo, self.btnGoClick)


        grid.addWidget(self.tabs, 2, 0, 1, 12)

        # grid.addWidget(QLabel('description:'), 3, 0)
        self.btnPicture = QPushButton('테스트')
        grid.addWidget(self.btnPicture, 3, 0)
        self.btnPicture.clicked.connect(self.btnTest_Click)

        self.btnPhoto = QPushButton('사진 관리')
        grid.addWidget(self.btnPhoto, 3, 1)
        self.btnPhoto.clicked.connect(self.btnPhoto_Click)

        self.btnDoWithFiles = QPushButton('Do With Files')
        grid.addWidget(self.btnDoWithFiles, 3, 2)
        self.btnDoWithFiles.clicked.connect(self.btnDoWithFiles_Click)

        self.btnFindFiles = QPushButton('파일 찾기')
        grid.addWidget(self.btnFindFiles, 3, 3)
        self.btnFindFiles.clicked.connect(self.btnFindFiles_Click)

        self.btnRSS = QPushButton('RSS')
        grid.addWidget(self.btnRSS, 3, 4)
        self.btnRSS.clicked.connect(self.btnRSS_Click)

        self.btnExcel = QPushButton('Excel')
        grid.addWidget(self.btnExcel, 3, 5)
        self.btnExcel.clicked.connect(self.btnExcel_Click)

        self.btnWord = QPushButton('Word')
        grid.addWidget(self.btnWord, 3, 5)
        self.btnWord.clicked.connect(self.btnWord_Click)

        self.btnPhoto2 = QPushButton('사진 관리2')
        grid.addWidget(self.btnPhoto2, 3, 6)
        self.btnPhoto2.clicked.connect(self.btnPhoto2_Click)

        self.btnDayWork = QPushButton('MyProject_DayWork')
        grid.addWidget(self.btnDayWork, 3, 7)
        self.btnDayWork.clicked.connect(self.btnDayWork_Click)


        self.tabs.currentChanged.connect(self.onChangeTab)  # changed!
        self.btnGo.clicked.connect(self.btnGoClick)
        self.btnBack.clicked.connect(self.btnBackClick)


        #상태진행바
        self.progressBar = QProgressBar(self)
        self.progressBar.setFormat('%v/%m (%p%)')
        self.progressBar.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        grid.addWidget(self.progressBar, 4, 0, 1, 12)


        #------------------------------------------------------------------------------
        #* 트리와 리스트뷰 추가
        # ------------------------------------------------------------------------------
        for i in range(0, self.tabs.count()):
            tab = self.tabs.widget(i)
            self.f_add_tree(tab, '')

        # Timer 설정
        self.timer = QTimer(self)
        self.timer.start(100)
        self.timer.timeout.connect(self.timeout_run)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.on_contextMenu)

        # ------------------------------------------------------------------------------
        # * 탭 마우스 클릭 이벤트 연결
        # ------------------------------------------------------------------------------
        self.tabs.installEventFilter(self)

    def eventFilter(self, object, event):
        # 마우스 오른쪽 버튼을 누를 경우 active로 변경하기 위해
        if object == self.tabs and \
                event.type() in [QEvent.MouseButtonPress,
                                 QEvent.MouseButtonRelease] and \
                event.button() == Qt.RightButton:
            print('**** 200')

            position = event.pos()
            tabIndex = self.tabs.tabBar().tabAt(position)
            print('********* tabIndex " ', tabIndex)

            self.tabs.setCurrentIndex(tabIndex)

            return True
        return False

    def on_contextMenu(self, position):
        print('**********MyExplorer on_contextMenu')

        menu = QMenu()

        root = QFileInfo(__file__).absolutePath()

        action_rename = QAction(QIcon(root + './img/explorer.png'), "Rename Tab(&R)", self, statusTip="rename")

        action_new_tab = QAction(QIcon(root + './img/explorer.png'), "New Tab(&N)", self, statusTip="New Tab")
        action_copy_tab = QAction(QIcon(root + './img/explorer.png'), "Copy Tab(&C)", self, statusTip="Copy Tab")

        print("* 현재위치 : ", os.getcwd())
        menu.addAction(action_rename)
        menu.addSeparator()
        menu.addAction(action_new_tab)
        menu.addAction(action_copy_tab)

        tabIndex = self.tabs.tabBar().tabAt(position)
        print('on_contextMenu : ', tabIndex)
        action = menu.exec_(self.mapToGlobal(position))

        if action == None:
            return

        elif action == action_rename:
            self.onRenameTab()

        elif action == action_new_tab:
            tab_new = QWidget()
            tab_new.my_cur_dir = "c:\\"
            self.tabs.addTab(tab_new, 'New')

        elif action == action_copy_tab:
            tab_new = QWidget()
            tab_new.my_cur_dir = self.txtUrl.text()
            self.tabs.addTab(tab_new, 'New')



    def btnExcel_Click(self):
        from openpyxl import Workbook

        cursor = CMyCursor()
        wb = Workbook()

        self.wb = wb

        del cursor
    def btnWord_Click(self):


        from mailmerge import MailMerge #pip install docx-mailmerge
        cursor = CMyCursor()

        template = 'template_mailmerge.docx'
        doc = MailMerge(template)

        print(doc.get_merge_fields())

        
        index = 3
        if index == 1:


            #삽입 - 빠른 문서 요소 - 필드 -MergeField
            doc.merge(title='Mr', reg_id = '555', familyname = 'han', givenname = 'honghee')
            doc.write('template_output_01.docx')
        elif index == 2:
            doc.merge(name='진영화학')

            sales_history = [{
                'prod_desc':'밤색구두',
                'price':'$10.00',
                'quantity': '2500',
                'total_purchases': '$25,000.00',
            },{
                'prod_desc': '밤색구두2',
                'price': '$10.00',
                'quantity': '2500',
                'total_purchases': '$25,000.00',
            }, {
                'prod_desc': '밤색구두3',
                'price': '$10.00',
                'quantity': '2500',
                'total_purchases': '$25,000.00',
            }, {
                'prod_desc': '밤색구두4',
                'price': '$10.004444',
                'quantity': '2500',
                'total_purchases': '$25,000.00',
            }
            ]

            doc.merge_rows('prod_desc', sales_history)
            doc.write('template_output_01.docx')
        elif index == 3:
            #워드를 파이썬으로 저장하기...
            import os
            from win32com.client import Dispatch

            wordapp = Dispatch("Word.Application")

            fpath = os.path.join(os.getcwd(), "template_output_01.docx")
            myDoc = wordapp.Documents.Open(FileName = fpath)

            pdf_path = os.path.join(os.getcwd(), "template_pdf_output_01.pdf")
            myDoc.SaveAs(pdf_path, FileFormat=17)

            myDoc.Close()
            wordapp.Quit()

    def f_add_tree(self, tab, dir):
        if hasattr(tab, 'treeView') == True: return

        # 탭 레이아웃 설정
        tab.layout = QHBoxLayout(self)
        # tab.layout.addWidget(self.pushButton1)

        # 스플리터
        splitter = QSplitter(Qt.Horizontal)

        # ------------------------------------------------------------------------------
        # * 트리뷰
        # ------------------------------------------------------------------------------
        treeView = MyTreeView(self, dir = dir, mytab = tab)
        splitter.addWidget(treeView)

        # ------------------------------------------------------------------------------
        # * 리스트 뷰
        # ------------------------------------------------------------------------------
        tableView = MyTableView(self, dir = dir, mytab = tab)
        splitter.addWidget(tableView)

        # 스플리터를 레이아웃에 추가...
        tab.layout.addWidget(splitter)
        tab.setLayout(tab.layout)

        # 리스트뷰를 트리뷰에 등록, 트리뷰를 리스트 뷰에 등록.
        treeView.tableView = tableView
        tableView.treeView = treeView

        # The Access point from tab....
        tab.treeView = treeView
        tab.tableView = tableView


    def btnRSS_Click(self):
        #self.f_send_rss()
        self.f_getAllTabDir()

    def f_send_rss(self):

        #schtasks /create /tn hanhongee_rss /sc minute /mo 10 /tr "d:/anaconda3/python.exe d:/newsreader.py"
        # 삭제 : schtasks /delete /tn hanhongee_rss /f
        import smtplib
        import feedparser
        from email.mime.text import MIMEText
        from email.header import Header

        # 관심 RSS feed 주소를 추가, 변경한다.
        rss_feeds = [
            'http://file.mk.co.kr/news/rss/rss_30100041.xml',
            'http://file.mk.co.kr/news/rss/rss_50300009.xml'
        ]

        # words of interest. 관심 단어
        WOI = ['금리', '대출', '가격', '리스크']

        out = []
        for feed in rss_feeds:
            d = feedparser.parse(feed)
            for entry in d.entries:
                for w in WOI:  # 관심 단어가 제목이나 요약에 있는지 살핀다
                    if w in entry['title'] or w in entry['summary']:
                        s = '* {} {}'.format(entry['title'], entry['link'])
                        out.append(s)
                        break
        message = '\n'.join(out)

        if message:
            # 메일 발송
            subject = 'RSS News'
            mail_from = mail_to = 'hanhonghee@gmail.com'
            id_ = 'hanhonghee@gmail.com'
            pw_ = 'h!an19845'

            smtp = smtplib.SMTP('smtp.gmail.com', 587)
            smtp.ehlo()
            smtp.starttls()
            smtp.login(id_, pw_)

            msg = MIMEText(message.encode('utf-8'), _subtype='plain', _charset='utf-8')
            msg['Subject'] = Header(subject.encode('utf-8'), 'utf-8')
            msg['From'] = mail_from
            msg['To'] = mail_to

            smtp.sendmail(mail_from, mail_to, msg.as_string())
            smtp.quit()

    def btnPhoto_Click(self):
        model, indexes = self.f_getCurModel()
        index = indexes[0]
        if model == None: return

        fpath = model.filePath(index)
        dlg = MyPhotoUI()
        dlg.setUrl(fpath)

        dlg.exec_()
        
    def btnPhoto2_Click(self):
        model, indexes = self.f_getCurModel()
        index = indexes[0]
        if model == None: return

        fpath = model.filePath(index)

        fpath = fpath.replace('/', '\\')
        dlg = MyPhotoUI2()
        dlg.setUrl(fpath)

        dlg.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
        dlg.setWindowFlag(Qt.WindowMaximizeButtonHint, True)


        dlg.exec_()


    def btnDayWork_Click(self):
        dlg = MyProject_DayWork()

        dlg.exec_()

    #* 현재 열린 모든 탭의 current directory 리스트 반환.
    #* 목적1 : 종료시 ini파일에 적는다.
    def f_getAllTabDir(self):
        cnt = self.tabs.count()

        tab_names = []
        dirs = []
        for i in range(0, cnt):
            tab = self.tabs.widget(i)
            my_dir = tab.my_cur_dir
            tab_name = self.tabs.tabText(i)

            tab_names.append(tab_name)
            dirs.append(my_dir)

        return tab_names, dirs


    def f_getCurDir(self):
        return self.txtUrl.text()

    def f_getCurModel(self, ofWhat = None):
        cur_tab_widget = self.getActiveTabWidget()
        model = None
        indexes = None
        widget = QtWidgets.QApplication.focusWidget()


        print('************', str(type(widget)))
        if ofWhat == 'TreeView':
            model = cur_tab_widget.treeView.myModel
            indexes = cur_tab_widget.treeView.selectionModel().selectedIndexes()

        elif str(type(widget)) == "<class 'PyQt5.QtWidgets.QTreeView'>":
            model = cur_tab_widget.treeView.myModel

            indexes = widget.selectionModel().selectedIndexes()
            #index = index[0]


        elif str(type(widget)) == "<class 'src.MyTableView.MyTableView'>":
            model = cur_tab_widget.tableView.myModel
            indexes = widget.selectionModel().selectedIndexes()
            #index = index[0]


        else:
            model = cur_tab_widget.treeView.myModel
            indexes = cur_tab_widget.treeView.selectedIndexes()

        return model, indexes

    def txtUrl_returnPressed(self):
        self.btnGoClick()

    #------------------------------------------------------------------------------
    # 최초 화면 처리 - 트리뷰의 첫번째 노드를 선택한다.
    # ------------------------------------------------------------------------------
    def timeout_run(self):
        self.timer.stop()

        cur_tab_widget = self.getActiveTabWidget()

        # index = cur_tab_widget.treeView.myModel.index(0, 0);
        # row = index.row()
        # #cur_tab_widget.treeView.selectionModel().setCurrentIndex(index, QItemSelectionModel.Select)
        # cur_tab_widget.treeView.selectionModel().select(index, QItemSelectionModel.ClearAndSelect)
        # cur_tab_widget.tableView.setFocus()


        self.txtUrl_returnPressed()

    def getActiveTabWidget(self):
        if self.tabs.count() == 0:
            return None

        cur_tab_index = self.tabs.currentIndex()
        cur_tab_widget = self.tabs.widget(cur_tab_index)

        return cur_tab_widget

    def onFileCopy(self):
        cur_tab_widget = self.getActiveTabWidget()
        if cur_tab_widget:
            cur_tab_widget.tableView.onFileCopy()


    def onFileCopyFileNameOnly(self):
        cur_tab_widget = self.getActiveTabWidget()
        if cur_tab_widget:
            cur_tab_widget.tableView.onFileCopyFileNameOnly()


    def onFilePaste(self):
        cur_tab_widget = self.getActiveTabWidget()
        if cur_tab_widget:
            cur_tab_widget.tableView.onFilePaste()

    def onDelete(self):
        cur_tab_widget = self.getActiveTabWidget()
        if cur_tab_widget:
            cur_tab_widget.tableView.onDelete()

    def onRenameFile(self):
        cur_tab_widget = self.getActiveTabWidget()
        if cur_tab_widget:
            cur_tab_widget.tableView.onRename()

    def onRenameTab(self):

        if self.tabs.count() == 0:
            return
        cur_tab_index = self.tabs.currentIndex()
        strTabText = self.tabs.tabText(cur_tab_index)

        text, res = MyLibDlg_InputDialog.f_make_QInputDialog(self, "탭 이름 바꾸기", "바꿀 탭 이름을 입력하세요.", QLineEdit.Normal, strTabText)
        if res:
            self.tabs.setTabText(cur_tab_index, text)


    #------------------------------------------------------------------------------
    #* 파일 속성
    # ------------------------------------------------------------------------------
    def onFileInfo(self):

        #* 현재 포커스가 있는 창의 모델과 인덱스를 얻어온다.
        model, indexes = self.f_getCurModel()

        #여러개의 index 중 첫번째를 가져옴
        index = indexes[0]
        if model == None: return

        # 모델에 인덱스를 넣어 path를 가져온다.
        fpath = model.filePath(index)


        dlg = MyFileInfo()
        dlg.setUrl(fpath)

        dlg.exec_()


    def btnTest_Click(self):
        pass
        # #------------------------------------------------------------------------------
        # #* 도스창의 output 받기
        # #------------------------------------------------------------------------------
        # from subprocess import Popen, PIPE
        #
        # pipe = Popen('dir', shell=True, stdout = PIPE)
        #
        # #print(pipe.stdout.read().decode('cp949')[:284])
        # print(pipe.stdout.read().decode('cp949'))

        # #------------------------------------------------------------------------------
        # #* 1. 스케쥴러 몇초후
        # #------------------------------------------------------------------------------
        # import sys
        # import sched
        #
        # def my_job(text="..."):
        #     print(text)
        #     sys.stdout.flush()
        #
        # s = sched.scheduler(time.time, time.sleep)
        # # (delay, priority, action, argument)
        # s.enter(5, 1, my_job)
        # s.enter(10, 1, my_job, argument=('good!', ))
        #
        # s.run() #blocking 된다...
        # print('done....')

        # # ------------------------------------------------------------------------------
        # # * 2. 스케쥴러 절대시간....
        # # ------------------------------------------------------------------------------
        # import sched
        # import time
        # scheduler = sched.scheduler(time.time, time.sleep)
        #
        # def print_event(name):
        #     print('EVENT:', time.time(), name)
        #
        # now = time.time()
        # print('START:', now)
        # scheduler.enterabs(now + 2, 2, print_event, ('first',))
        # scheduler.enterabs(now + 5, 1, print_event, ('second',))
        # scheduler.run()

        # # ------------------------------------------------------------------------------
        # # * 3. non blocking... 몇 초 후에 실행하기...
        # # ------------------------------------------------------------------------------
        # import threading
        # import time
        #
        # def my_job(text):
        #     print(text)
        #
        # timer = threading.Timer(5, my_job, ('* hanhonghee....', ))
        # timer.start()
        # print('other works continued....')

        # # ------------------------------------------------------------------------------
        # # * 4. 지정된 시간에 실행하기...
        # # ------------------------------------------------------------------------------
        # import threading
        # import time
        #
        # def run_it_at(at, func, args=()):
        #     t = time.strptime(at, '%Y-%m-%d %H:%M:%S')
        #     t = time.mktime(t)  #지정된 시간을 숫자시간으로 변환
        #     diff_sec = t - time.time() #현재 시간과의 차이... 즉 대기시간(초)
        #
        #     print(diff_sec)
        #
        #     mythread = threading.Timer(diff_sec, func, args)
        #     mythread.start()
        #
        # def my_job(text):
        #     print(text)
        #
        # run_it_at('2021-04-16 15:44:15', my_job, ('hanhonghee.... 만세....', ))
        # print('* this is other job....')

        # ------------------------------------------------------------------------------
        #* 5. 주기적으로 실행하기...
        # ------------------------------------------------------------------------------
        # import schedule
        # import time
        #
        # def job(msg = "I'm hanhonghee....."):
        #     print(msg)
        #
        # schedule.every().seconds.do(job) #매 1초마다 실행...
        # schedule.every(5).seconds.do(job, ('* 5 초에 한번 실행....', ))
        #
        # schedule.every(1).minutes.do(job) #1분에 한번
        # schedule.every().day.at("15:50").do(job, ("15:50...", ))
        #
        # schedule.every().day.at("15:51").do(job, ("15:50...",))
        #
        # schedule.every().day.at("15:52").do(job, ("15:50...",))
        #
        # schedule.every().day.at("15:53").do(job, ("15:50...",))
        #
        # schedule.every(5).to(10).seconds.do(job, ("I'm random(5 sec to 10)", ))
        #
        # schedule.every().wednesday.at("13:15").do(job) #수요일 13:15분마다...
        #
        # while True:
        #     schedule.run_pending() #대기중인 작업이 있다면 처리한다.
        #     time.sleep(1)

        # ------------------------------------------------------------------------------
        #* 6. 윈도우 작업 스케쥴러...
        # ------------------------------------------------------------------------------
        #schtasks
        #* 1분마다 계산기 실행.
        #schtasks /create /tn monitor /sc minute /mo 1 /tr calc

        #* 계산기 예약작업 삭제
        #schtasks /delete /tn monitor /f

        #/tn : taskname, 작업이름 지정정
        #/sc: scheduler, 스케쥴 빈도 설정. (MINUTE, HOURLY, DAILY, WEEKLY, MONTHLY, ONCE, ONSTART, ONLOGON, ONIDLE, ONEVENT)
        #/mo: modifier, 반복주기값을 지정(단위는 /sc 값에 따라서 달라진다. MINUTE, HOURLY, DAILY, WEEKLY, MONTHLY일때만 의미있음.)
        #/sd : startdate, 작업 시작 철 번째 날짜. 형식은 yyyy/mm/dd. 기본값은 현재날짜(오늘)
        #/ed : enddate, 작업의 종료 일자. 형식은 yyyy/mm/dd.
        #/st : starttime, 작업 시작시간. 형식은 HH:mm(24시간 형식). 지정하지 않으면 현재 시간.
        #/et : endtime, 작업 종료시간. 형식은 HH:mm(24시간 형식)
        #/d : 요일(MON, TUE, WD, THU, FRI, SAT, SUN) 혹은 날짜(1-31)
        #/k : KILL, 작업 종료 시간이 되면, 실행 중인 프로그램을 강제 종료한다.
        #/it : 사용자가 로그온되어 있는 경우에만 실행한다.
        #/tr : taskrun, 실행할 프로그램
        #/f : force, 작업이 수행되는 중이라도 임무를 수행한다.

        #매분 파이썬 스크립트 실행.
        #schtasks /create /tn monitor /sc minute "d:\anaconda3\python.exe d:\monitor.py"

        # 매일 아침 9시 계산기 실행.
        # schtasks /create /tn monitor /sc daily /st 09:00 /tr calc

        # 매주 월요일 아침 9시 계산기 실행.
        # schtasks /create /tn monitor /sc weekly /d Mon /st 09:00 /tr calc

        # 매월 1일 아침 9시 계산기 실행.
        # schtasks /create /tn monitor /sc monthly /d 1 /st 09:00 /tr calc

        # 지정된 일시에 단 한번만 계산기 실행.
        # schtasks /create /tn monitor /sc once /sd 2021-04-16 /st 09:00 /tr calc

        # 사용자 gslee가 로그온할때 계산기 실행. 단 명령행 프롬프틀 관리자 모드로 실행해야 함.
        # schtasks /create /tn onlogon /sc ONLOGON /tr notepad.exe
        # schtasks /create /tn my_onstart /sc ONSTART /tr calc /ru icis-han



    def btnDoWithFiles_Click(self):

        model, indexes = self.f_getCurModel()
        index = indexes[0]
        if model == None: return

        fpath = model.filePath(index)

        dlg = MyDoWithFiles()
        dlg.setUrl(fpath)

        dlg.exec_()

    def btnFindFiles_Click(self):

        model, indexes = self.f_getCurModel()
        index = indexes[0]
        if model == None: return

        fpath = model.filePath(index)

        dlg = MyFindFiles()
        dlg.setUrl(fpath)

        dlg.exec_()

    #트리뷰 디렉토리 지정
    def btnGoClick(self):

        cur_tab_widget = self.getActiveTabWidget()

        if not cur_tab_widget:
            return

        txtUrl = self.txtUrl.text()
        index = cur_tab_widget.treeView.myModel.index(txtUrl, 0);
        row = index.row()

        #cur_tab_widget.treeView.selectionModel().setCurrentIndex(index, QItemSelectionModel.Select)
        cur_tab_widget.treeView.selectionModel().select(index, QItemSelectionModel.ClearAndSelect)

    def btnBackClick(self):

        if len(self.url_back) < 2: return

        cur_tab_widget = self.getActiveTabWidget()

        #txtUrl = self.txtUrl.text()
        index = cur_tab_widget.treeView.myModel.index(self.url_back[-2], 0);
        row = index.row()

        #cur_tab_widget.treeView.selectionModel().setCurrentIndex(index, QItemSelectionModel.Select)
        cur_tab_widget.treeView.selectionModel().select(index, QItemSelectionModel.ClearAndSelect)

    # @pyqtSlot()
    def onChangeTab(self, i):  # changed!
        if i < 0:
            return

        tab = self.tabs.widget(i)

        # 지연된 로드. 최초 포커스때 widget 추가
        if hasattr(tab, 'treeView') == False:
            self.f_add_tree(tab, '')

        self.txtUrl.setText(tab.my_cur_dir)
        self.txtUrl_returnPressed()

        # self.f_add_tree(tab2)

        # QMessageBox.critical(self, "Tab Index Changed!",
        #                               "Current Tab Index: %d" % i)  # changed!

if __name__ == "__main__":
    import sys




    app = QApplication(sys.argv)
    ex = CMyExplorer()
