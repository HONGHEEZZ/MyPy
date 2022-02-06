
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
from distutils.dir_util import copy_tree


from . MyFindFiles import *

from . MyCursor import *
from . MyClipboard import *

#여기서 내 Library path를 추가한다.
sys.path.append('../MyLib')
import MyLibDlg_InputDialog

class MyTableView(QTableView):
    def __init__(self, parent=None, dir='', mytab = None):
        super(MyTableView, self).__init__(parent)
        self.parent = parent
        self.dir = dir
        self.mytab = mytab
        self.myModel = None

        self.setSortingEnabled(True)

        self.initUI()

    def initUI(self):
        self.setShowGrid(False)
        self.setWordWrap(False);
        self.setSelectionBehavior(QAbstractItemView.SelectRows)  # row 전체를 선택하도록
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)  #
        self.setTabKeyNavigation(False)
        # ensureVisbible(True)

        self.verticalHeader().setDefaultSectionSize(20)  # 라인 높이 조정....
        self.verticalHeader().setVisible(False)  # 라인번호 제거

        myModel = QFileSystemModel()
        myModel.setRootPath(self.dir)
        self.myModel = myModel
        self.setModel(self.myModel)

        # 오른쪽 마우스 클릭
        # 컨텍스트 메뉴
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.on_tblFiles_contextMenu)

        # 이벤트 핸들러 등록
        self.doubleClicked.connect(self.on_tableView_doubleClicked)

    # ------------------------------------------------------------------------------
    # * 창의 크기가 바뀌면 자동으로 호출되는 이벤트
    # ------------------------------------------------------------------------------
    def resizeEvent(self, event):
        # 칼럼 너비 조정
        self.f_set_colwidth_auto()

    #------------------------------------------------------------------------------
    #* 칼럼너비 자동 조정
    # ------------------------------------------------------------------------------
    def f_set_colwidth_auto(self):
        header = self.horizontalHeader()
        twidth = header.width()
        myWidths = []
        for column in range(header.count()):
            header.setSectionResizeMode(column,
                        QHeaderView.ResizeToContents)
            size = header.sectionSize(column)
            myWidths.append(size)

        wfactor = twidth / sum(myWidths)

        for column in range(header.count()):
            header.setSectionResizeMode(column,
                    QHeaderView.Interactive)
            header.resizeSection(column, myWidths[column] * wfactor)


    def keyPressEvent(self, event):
        key = event.key()

        if key == Qt.Key_Return or key == Qt.Key_Enter:
            # Process current item here
            print("I'm MyTableView.... Return................")

            index = self.selectionModel().selectedIndexes()
            self.f_tableView_doubleClicked(index[0])

        if key == Qt.Key_Backspace:
            self.parent.btnBackClick()

        else:
            super(MyTableView, self).keyPressEvent(event)


    def on_tblFiles_contextMenu(self, position):


        #포지션에 있는 하나만 선택....
        index = self.indexAt(position)

        #선택되어있는 전체 선택..
        # indexes = tblFiles.selectedIndexes()
        # index = indexes[0]


        fname = self.myModel.fileName(index)

        fdir = self.parent.txtUrl.text()
        fpath = os.path.join(fdir, fname)

        # item_range = QTableWidgetSelectionRange(0, c, tblFiles.rowCount() - 1, c)
        # tblFiles.setRangeSelected(item_range, True)

        menu = QMenu()

        root = QFileInfo(__file__).absolutePath()

        # HEdit으로 열기
        open_with_hedit = QAction(QIcon(root + '/..img/HEdit.ico'), "HEdit으로 열기(&H)", self, statusTip="HEdit으로 열기")


        open_with_explorer = QAction(QIcon(root + '/../img/explorer.png'), "탐색기로 열기(&E)", self, statusTip="탐색기로 열기")
        #open_with_explorer = QAction(QIcon("d:/explorer.png"), "탐색기로 열기(&E)", self, statusTip="탐색기로 열기")
        open_file = QAction(QIcon(root + '/../img/openfile.png'), "파일 열기(&O)", self, statusTip="파일 열기")
        act_edit_delete = QAction(QIcon(root + '/../img/delete.png'), "Delete(&D)", self, statusTip="FileDelete")
        act_edit_rename = QAction(QIcon(root + '/../img/rename_file.png'), "Rename(&R)", self, statusTip="FileRename")
        act_new_folder = QAction(QIcon(root + '/../img/newfolder.png'), "New Foler(&N)", self, statusTip="New Folder")

        act_new_file = QAction(QIcon(root + '/../img/new_file.png'), "New File(&F)", self, statusTip="New File")

        act_cmd = QAction(QIcon(root + '/../img/command-window.png'), "Command(&C)", self, statusTip="Command창 열기")

        act_file_info = QAction(QIcon(root + '/../img/info.png'), "File Info(&I)", self, statusTip="File Info")


        open_calc = None
        new_file_text = None

        print("* 현재위치 : ", os.getcwd())
        if not self.indexAt(position).isValid():

            menu.addAction(open_with_hedit)

            menu.addSeparator()
            menu.addAction(act_new_folder)
            menu.addAction(act_new_file)

            menu.addSeparator()
            menu.addAction(act_cmd)


            menu.addSeparator()
            open_calc = menu.addAction("Open Calc")

        else:
            menu.addAction(open_with_hedit)

            menu.addSeparator()

            menu.addAction(act_new_folder)
            menu.addSeparator()

            menu.addAction(open_with_explorer)
            menu.addAction(open_file)

            menu.addSeparator()
            menu.addAction(act_edit_delete)
            menu.addAction(act_edit_rename)



            menu.addSeparator()
            menu.addAction(act_cmd)

            menu.addSeparator()
            menu.addAction(act_file_info)


        action = menu.exec_(self.viewport().mapToGlobal(position))

        if action == None:
            return

        elif action == act_new_folder:
            self.onNewFolder()

        elif action == open_with_hedit:
            from subprocess import Popen

            Popen([r'notepad.exe', fpath])

        elif action == act_new_file:

            model, indexes = self.parent.f_getCurModel('TreeView')
            index = indexes[0]
            if model == None: return

            os.chdir(model.filePath(index))
            cwd = os.getcwd()


            dir = model.filePath(index)
            fname = os.path.join(dir, "New File")
            strExt = ".txt"

            if os.path.exists(fname+strExt) :
                index = 2
                while True:
                    new_fname = fname + str(index)
                    if not os.path.exists(new_fname+strExt):
                        fname = new_fname
                        break
                    else:
                        index += 1


            f = open(fname+strExt, 'w', encoding="UTF8")
            f.close()

            # 새로 만든 파일을 선택해준다.
            fullPath = os.path.join(dir, fname + strExt)
            self.f_select_node(fullPath, QItemSelectionModel.Select)

        elif action == open_calc:
            from subprocess import Popen
            Popen('calc')

        elif action == open_file:
            os.startfile(fpath)

        elif action == open_with_explorer:
            os.startfile(fpath)

        elif action == act_edit_delete:
            self.onDelete()

        elif action == act_edit_rename:
            self.onRename()

        elif action == act_file_info:
            self.parent.onFileInfo()

        #------------------------------------------------------------------------------
        #* 도스창 열기
        #------------------------------------------------------------------------------
        elif action == act_cmd:
            #선택한 노드가 dir이면 path로 지정
            if os.path.isdir(fpath):
                os.chdir(fpath)
            else:
                #선택한 노드가 파일인 경우
                os.chdir(fdir)
                
            os.system("start")


    def onNewFolder(self):

        model, indexes = self.parent.f_getCurModel('TreeView')
        index = indexes[0]
        if model == None: return

        os.chdir(model.filePath(index))
        cwd = os.getcwd()
        print('***********cwd : ', cwd, ", filename : ", model.filePath(index))

        fname = model.fileName(index)
        text, res = MyLibDlg_InputDialog.f_make_QInputDialog(self, "새 폴더 만들기", "만들 폴더명을 입력하세요.", QLineEdit.Normal)

        if res:
            while True:
                self.ok = True

                for i in os.listdir(os.getcwd()):
                    print(i)
                    if i == text:
                        text, res = MyLibDlg_InputDialog.f_make_QInputDialog(self, "중복 오류", "이미 존재하는 폴더명임. 바꿀 이름을 다시 입력하세요.",
                                                         QLineEdit.Normal, text)
                        if not res:
                            return
                        self.ok = False

                if self.ok:
                    break;
            os.mkdir(text)

    def onRename(self):

        model, indexes = self.parent.f_getCurModel()
        index = indexes[0]
        if model == None: return

        os.chdir(model.filePath(model.parent(index)))
        cwd = os.getcwd()
        print('***********cwd : ', cwd, ", filename : ", model.filePath(index))

        fname = model.fileName(index)
        text, res = MyLibDlg_InputDialog.f_make_QInputDialog(self, "이름 바꾸기", "바꿀 이름을 입력하세요.", QLineEdit.Normal, fname)

        if res:
            while True:
                self.ok = True

                for i in os.listdir(os.getcwd()):
                    print(i)
                    if i == text:
                        text, res = MyLibDlg_InputDialog.f_make_QInputDialog(self, "중복 오류", "이미 존재하는 파일명임. 바꿀 이름을 다시 입력하세요.",
                                                         QLineEdit.Normal, fname)
                        if not res:
                            return
                        self.ok = False

                if self.ok:
                    break;
            os.rename(fname, text)

    def onFileCopy(self):

        model, indexes = self.parent.f_getCurModel()
        if model == None: return

        fname = model.fileName(indexes[0])

        # f_getCurModel()하면 중복으로 1-> 4개씩 나옴. set으로 하나로 바꾸는 작업함....
        fset = set()
        for index in indexes:
            fpath = model.filePath(index)

            #Windows는 \\를 기본으로 함.
            fpath = fpath.replace('/', '\\')
            fset.add(fpath)

        myClip = CMyClipboard()
        flist = list(fset)
        myClip.set_clip_files(flist)


    def onFileCopyFileNameOnly(self):
        model, indexes = self.parent.f_getCurModel()
        if model == None: return

        fname = model.fileName(indexes[0])

        # f_getCurModel()하면 중복으로 1줄에 4개씩 나옴. set으로 하나로 바꾸는 작업 함...
        fset = set()
        for index in indexes:
            fpath = model.filePath(index)

            # Windows는 \\를 기본으로 함.
            fpath = fpath.replace('/', '\\')
            fname = os.path.split(fpath)
            fset.add(fname[1])

        clip = CMyClipboard()
        flist = list(fset)
        str = clip.set_clip_strings(flist)

        QMessageBox.information(self, '알림', str, QMessageBox.Yes)

    # ------------------------------------------------------------------------------
    # * 동일 폴더에서 붙여 넣는 경우 - 복사본 (2) 와 같이 파일명 변경해줌
    # ------------------------------------------------------------------------------
    def f_get_copy_file_name(self, src_dir, src_file, target_dir):
        fname_only, ext = os.path.splitext(src_file)

        index = 1

        while True:
            new_target_file = f"{fname_only} - 복사본({index}){ext}"
            targetFull = os.path.join(target_dir, new_target_file)

            # ------------------------------------------------------------------------------
            # * 존재하지 않음. 루프 탈출
            # ------------------------------------------------------------------------------
            if not os.path.exists(targetFull):
                break

            index += 1

        return new_target_file

    # ------------------------------------------------------------------------------
    # * copy 파일
    # ------------------------------------------------------------------------------
    def f_copy_file(self, srcFull, target_dir, prev_msgbox_rtn):
        msgbox_rtn = prev_msgbox_rtn

        src_dir, src_file = os.path.split(srcFull)

        src_dir, src_file = os.path.split(srcFull)

        targetFull = os.path.join(target_dir, src_file)

        # ------------------------------------------------------------------------------
        # 1. 단순 카피
        # ------------------------------------------------------------------------------
        if not os.path.exists(targetFull):
            shutil.copy(srcFull, targetFull)

        # ------------------------------------------------------------------------------
        # 2. 파일명 이미 존재시
        # ------------------------------------------------------------------------------
        else:
            # ------------------------------------------------------------------------------
            # 2.1 계속 덮어쓰기.
            # ------------------------------------------------------------------------------
            if prev_msgbox_rtn == QMessageBox.YesToAll:
                shutil.copy2(srcFull, targetFull)

            # ------------------------------------------------------------------------------
            # 2.2 디렉토리가 다르면
            # ------------------------------------------------------------------------------
            elif src_dir != target_dir:
                msgbox_rtn = QMessageBox.question(self, "덮어쓰기확인", f"[{src_file}] 파일이 이미 있습니다. 덮어쓰시겠습니까?",
                                    QMessageBox.Yes | QMessageBox.YesToAll | QMessageBox.No | QMessageBox.Cancel)

                if msgbox_rtn == QMessageBox.Yes or msgbox_rtn == QMessageBox.YesToAll:
                    shutil.copy2(srcFull, targetFull)

            # ------------------------------------------------------------------------------
            # 2.3 같은 Directory에 같은 파일이면
            # ------------------------------------------------------------------------------
            else:

                # ------------------------------------------------------------------------------
                # - 복사본 (2) 와 같이 파일명을 생성함.
                # ------------------------------------------------------------------------------
                new_file_name = self.f_get_copy_file_name(src_dir, src_file, target_dir)

                targetFull = os.path.join(target_dir, new_file_name)
                shutil.copy2(srcFull, targetFull)

        # ------------------------------------------------------------------------------
        # 방금 붙여 넣은 선택해준다.
        # ------------------------------------------------------------------------------
        self.f_select_node(targetFull, QItemSelectionModel.Select)

        return msgbox_rtn

    # ------------------------------------------------------------------------------
    # 리스트뷰의 노드를 선택/해제한다.
    # ------------------------------------------------------------------------------
    def f_select_node(self, urlFull, selctionMode = QItemSelectionModel.Select):

        index = self.myModel.index(urlFull, 0)
        row = index.row()
        self.selectionModel().select(index, selctionMode)

    #------------------------------------------------------------------------------
    #* 쓰레드 처리 필요...
    # ------------------------------------------------------------------------------
    def onFilePaste(self):
        clip = CMyClipboard()
        sources= clip.get_clip_files()

        # ------------------------------------------------------------------------------
        #* 타겟 디렉토리 추출
        # ------------------------------------------------------------------------------
        target_dir = self.parent.f_getCurDir()

        # ------------------------------------------------------------------------------
        # *타겟 디렉토리의 파일선택
        # ------------------------------------------------------------------------------
        self.f_select_node(target_dir, QItemSelectionModel.Clear)

        # ------------------------------------------------------------------------------
        #* Multi 파일 처리
        #  .- srcFull, targetFull : source full file name
        #  .- src_dri, target_dir : source dir, target dir
        #  .- src_file, target_file : source file target file
        # ------------------------------------------------------------------------------
        msgbox_rtn = None

        for srcFull in sources:
            # ------------------------------------------------------------------------------
            # 1. 파일인 경우
            # ------------------------------------------------------------------------------
            if os.path.isfile(srcFull):
                msgbox_rtn = self.f_copy_file(srcFull, target_dir, msgbox_rtn)

                # ------------------------------------------------------------------------------
                # * 취소면 break
                # ------------------------------------------------------------------------------
                if msgbox_rtn == QMessageBox.Cancel:
                    break

            # ------------------------------------------------------------------------------
            # 2. s디렉토리인 경우
            # ------------------------------------------------------------------------------
            elif os.path.isdir(srcFull):
                end_node = srcFull.split('\\')[-1]
                target = os.path.join(target_dir, end_node)
                copy_tree(srcFull, target)

            # 그외
            else:
                rtn = QMessageBox.information(self, "파일확인", f"[{srcFull}] is not a file, nor directory...",
                                              QMessageBox.Yes | QMessageBox.Cancel)
                if rtn == QMessageBox.Cancel:
                    break

    def onDelete(self):

        model, indexes = self.parent.f_getCurModel()
        if model == None: return

        fname = model.fileName(indexes[0])

        ret = QMessageBox.question(self, '확인', f'선택된 [{fname}]등 총 [{int(len(indexes)/4)}] 개의 파일 혹은 폴더를 삭제하시겠습니까?')
        if ret == QMessageBox.No: return


        for index in indexes:
            fpath = model.filePath(index)

            if model.isDir(index):
                # 여기 버그 있음... 삭제 안될때 있다. 지금은 귀찮다... 2021.04.16
                #model.rmdir(index)
                shutil.rmtree(fpath, ignore_errors=True)
            else:
                model.remove(index)


    @pyqtSlot(QtCore.QModelIndex)
    def on_tableView_doubleClicked(self, index):
        self.f_tableView_doubleClicked(index)

    def f_tableView_doubleClicked(self, index):

        treeView = self.treeView

        # 리스트뷰에서 더블클릭했다. 폴더라면 트리뷰를 펼친다....
        cur_treeview_index = treeView.selectedIndexes()[0]
        treeView.expand(cur_treeview_index)

        model = self.myModel

        # indexItem = model.index(index.row(), 0, index.parent())

        fileName = model.fileName(index)
        filePath = model.filePath(index)

        # full_name = os.path.join(filePath, fileName)

        if os.path.isdir(filePath):
            treeView.setCurrentIndex(treeView.myModel.index(filePath))
            treeView.scrollTo(treeView.myModel.index(filePath))

        elif os.path.isfile(filePath):

            cursor = CMyCursor()
            win32api.ShellExecute(0, 'open', filePath, None, None, 1)
            del cursor
        else:
            print("f_tableView_doubleClicked() else.....")

