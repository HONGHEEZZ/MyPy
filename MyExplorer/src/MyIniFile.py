from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from src.MyExplorer import *

import configparser

class CMyIniFile():
    def __init__(self, myMainWindow, config_file_name = None):
        self.myMainWindow = myMainWindow
        self.config_file_name = config_file_name

        self.config = configparser.ConfigParser()
        self.inifile_exist = False

        if config_file_name:
            config_file_dir = os.getcwd()
            self.config_file_name = os.path.join(config_file_dir, config_file_name)
            self.set_init_file(self.config_file_name)

    #------------------------------------------------------------------------------
    #* init 파일명을 지정한다.
    #------------------------------------------------------------------------------
    def set_init_file(self, myFile):

        self.myFile = myFile

        # 파일 존재 여부 체크
        self.f_check_inifile_exist()

        # 파일이 있으면 읽는다.
        if self.inifile_exist:
            # ini 파일 읽기
            read_ok = self.config.read(self.config_file_name)  # read_ok는 배열임


    #ini 파일이 존재하는지 체크
    def f_check_inifile_exist(self):
        if self.myFile:
            read_ok = self.config.read(self.config_file_name)  # read_ok는 배열임

            if read_ok:
                self.inifile_exist = True


    def save(self, myWidget):
        # config = myWidget.config
        # * 새로 생성해야 완전히 새로 만들 수 있다.
        config = configparser.ConfigParser()

        # ------------------------------------------------------------------------------
        # * 위치. 너비.
        # ------------------------------------------------------------------------------
        rect = myWidget.geometry()
        x = rect.x()
        y = rect.y()
        w = rect.width()
        h = rect.height()

        config['POSITION'] = {}

        # QtCore.Qt.WindowMaximized
        win_state = int(myWidget.windowState())
        config['POSITION']['WINDOW_STATE'] = str(win_state)

        config['POSITION']['x'] = str(x)
        config['POSITION']['y'] = str(y)
        config['POSITION']['w'] = str(w)
        config['POSITION']['h'] = str(h)

        config['POSITION']['geometry'] = str(myWidget.saveGeometry())
        config['POSITION']['windowState'] = str(myWidget.saveState())

        # QMdiSubWindow
        mdiSubWindows = myWidget.mdiArea.subWindowList()

        config['GLOBAL'] = {}
        config['GLOBAL']['MDI_SUBWINDOW_COUNT'] = str(len(mdiSubWindows))

        active_subwindow_index = myWidget.getActiveSubWindowIndex()
        config['GLOBAL']['active_subwindow_index'] = str(active_subwindow_index)

        mdi_index = 0
        for mdiSubWindow in mdiSubWindows:

            strSection = f'MDI_SUBWINDOW_{mdi_index}'
            config[strSection] = {}

            # MDI 탭 타이틀
            strMdiTabTitle = mdiSubWindow.windowTitle()
            config[strSection]['MDI_TAB_TITLE'] = strMdiTabTitle

            explorer = mdiSubWindow.widget()

            # 각 탭의 탭 이름/디렉토리....
            tab_names, dirs = explorer.f_getAllTabDir()
            config[strSection]['TAB_COUNT'] = str(len(tab_names))

            for tab_index in range(len(tab_names)):
                tab_name = f"tab_name_{tab_index}"
                dir_name = f"directory_{tab_index}"
                config[strSection][tab_name] = tab_names[tab_index]
                config[strSection][dir_name] = dirs[tab_index]

            mdi_index += 1

        # ------------------------------------------------------------------------------
        # * config 파일 저장
        # ------------------------------------------------------------------------------
        with open(myWidget.config_file_name, 'w') as configfile:
            config.write(configfile)

    def f_config_position_default(self):
        # window 중앙에 위치시킴
        self.setCentralWidget(self.mdiArea)
        self.resize(1200, 800)




    def load_position(self, myWidget):
        config = self.config


        if self.inifile_exist == False:
            return


        # MDI 기본설정
        myWidget.setWindowTitle("myExplorer")

        # window 중앙에 위치시킴
        myWidget.setCentralWidget(myWidget.mdiArea)

        root = QFileInfo(__file__).absolutePath()
        myWidget.setWindowIcon((QIcon(root + './img/main.png')))

        myWidget.resize(1200, 800)

        # 수평/수직 스크롤 사용
        myWidget.mdiArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        myWidget.mdiArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        if config.has_option('POSITION', 'geometry'):
            geometry = config['POSITION']['geometry']
            geometry = eval(geometry)

            windowState = config['POSITION']['windowState']
            windowState = eval(windowState)

            myWidget.restoreGeometry(geometry)
            myWidget.restoreState(windowState)

        # # ini 파일이 없으면 return
        # if len(read_ok) == 0:
        #     myWidget.f_config_position_default()
        # else:
        #     x =config['POSITION']['x']
        #     y =config['POSITION']['y']
        #     w =config['POSITION']['w']
        #     h =config['POSITION']['h']
        #
        #     x = int(x)
        #     y = int(y)
        #     w = int(w)
        #     h = int(h)
        #
        #     rect = QtCore.QRect(x, y, w, h)
        #     myWidget.setGeometry(rect)
        #
        #     win_state = config['POSITION']['WINDOW_STATE']
        #     if win_state == '2':
        #         myWidget.setWindowState(QtCore.Qt.WindowMaximized)

    # ------------------------------------------------------------------------------
    # * ini 파일에서 설정 읽어오기
    # ------------------------------------------------------------------------------
    def load_mdi(self, myWidget):
        config = self.config

        if self.inifile_exist == False:
            return 0

        # mid subwindow 개수
        mdi_subwindow_cnt = 0
        strCnt = config['GLOBAL']['mdi_subwindow_count']

        # 개수가 있을때만 처리...
        if strCnt:
            mdi_subwindow_cnt = int(strCnt)



        if mdi_subwindow_cnt <= 0:
            return 0

        for mdi_index in range(mdi_subwindow_cnt):
            strSection = f'MDI_SUBWINDOW_{mdi_index}'
            strMdiTabTitle = config[strSection]['MDI_TAB_TITLE']

            # myform = CMyExplorer(self, config[strSection])
            # # QMdiSubWindow
            # mdiSubWindow = myWidget.mdiArea.addSubWindow(myform)
            #
            #
            # mdiSubWindow.setWindowTitle(strMdiTabTitle)

            # * mdi subwindow 생성 / 탭이름 주기
            new_mdiSubWindow = QMdiSubWindow()
            new_mdiSubWindow.setWindowTitle(strMdiTabTitle)

            my_explorer = CMyExplorer(self.myMainWindow, config[strSection])

            # mdi에 위젯 붙이디....
            new_mdiSubWindow.setWidget(my_explorer)

            myWidget.mdiArea.addSubWindow(new_mdiSubWindow)

            new_mdiSubWindow.showMaximized()

            # 오른쪽 마우스 클릭
            # 컨텍스트 메뉴
            new_mdiSubWindow.setContextMenuPolicy(Qt.CustomContextMenu)
            new_mdiSubWindow.customContextMenuRequested.connect(myWidget.on_contextMenu)

        str_active_subwindow_index = config['GLOBAL']['active_subwindow_index']
        active_subwindow_index = int(str_active_subwindow_index)

        # acitve 윈도우 설정
        myWidget.setActiveSubWindowByIndex(active_subwindow_index)

        # subwindow 개수를 돌려준다.
        return mdi_subwindow_cnt