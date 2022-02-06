
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

from src.MyFindFiles import *

from src.MyCursor import *


class MyTreeView(QTreeView):
    def __init__(self, parent=None, dir='', mytab = None, tableView = None):
        super(MyTreeView, self).__init__(parent)
        self.parent = parent
        self.dir = dir
        self.mytab = mytab
        self.myModel = None
        self.tableView = tableView

        self.initUI()

    def initUI(self):
        model = QFileSystemModel()
        # model.setRootPath(QDir.rootPath())

        model.setFilter(QtCore.QDir.AllDirs | QtCore.QDir.NoDotAndDotDot)
        model.setRootPath(self.dir)

        self.setModel(model)
        self.myModel = model

        # 컨텍스트 메뉴
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.on_treeView_contextMenu)

        # * 이걸해야 선택된 폴더가 자동으로 펴진다.
        self.setSelectionBehavior(QAbstractItemView.SelectRows)

        # 이벤트 핸들러 등록
        self.clicked.connect(self.on_treeView_clicked)

        selmodel = self.selectionModel()
        selmodel.selectionChanged.connect(self.on_treeView_selectionChanged)
        selmodel.treeView = self

    # @pyqtSlot(QtCore.QModelIndex)
    def on_treeView_selectionChanged(self, selected, deselected):
        itemSelectionModel = self.sender()

        #cur_tab = self.parent.getActiveTab()

        indexes = selected.indexes()
        if len(indexes) == 0:
            index = self.myModel.index(self.mytab.my_cur_dir, 0);
        else:
            index = selected.indexes()[0]

        self.f_treeView_clicked(index)

    def f_treeView_clicked(self,index):
        cursor = CMyCursor()

        tableView = self.tableView
        model = self.myModel

        #선택된 노드가 보이도록 처리
        self.scrollTo(index, QAbstractItemView.EnsureVisible)


        row = index.row()
        myparent = index.parent()
        myrow2 = myparent.row()
        indexItem = model.index(row, 0, index.parent())

        fileName = model.fileName(indexItem)
        filePath = model.filePath(indexItem)

        #* /를 \\로 변경
        filePath = filePath.replace("/", "\\")

        # 리스트뷰
        tableView.setRootIndex(tableView.myModel.index(filePath))
        self.parent.url_back.append(filePath)


        # * 리스트뷰 첫행을 선택해줌...
        # * 윗 구문 setRootIndex가 먹힌 후 이것을 타는지 확인필요함.......
        index = tableView.model().index(0, 0)
        row = index.row()
        self.tableView.selectionModel().setCurrentIndex(index, QItemSelectionModel.Select | QItemSelectionModel.Rows)
        self.tableView.selectionModel().select(index, QItemSelectionModel.ClearAndSelect)


        # 칼럼 너비 자동 조절...
        self.resizeColumnToContents(0)

        # 칼럼 너비 조정
        self.tableView.f_set_colwidth_auto()

        # 텍스트 박스 directory 바꿈
        self.parent.txtUrl.setText(filePath)
        self.mytab.my_cur_dir = filePath

        # # 테이블 뷰 첫번째 항목을 선택...
        # index = treeView.tableView.model().index(0, 0)
        # row = index.row()
        # treeView.tableView.selectionModel().setCurrentIndex(index, QItemSelectionModel.Select)

        del cursor
    @pyqtSlot(QtCore.QModelIndex)
    def on_treeView_clicked(self, index):
        pass

    def on_treeView_contextMenu(self, position):


        indexes = self.selectedIndexes()
        if len(indexes) > 0:

            level = 0
            index = indexes[0]
            while index.parent().isValid():
                index = index.parent()
                level += 1

        menu = QMenu()
        action_empty = action_level0 = action_level1 = action_level2 = None
        if not self.indexAt(position).isValid():
            action_empty = menu.addAction(self.tr("Empty Area..."))
        elif level == 0:
            action_level0 = menu.addAction(self.tr("Edit person"))
        elif level == 1:
            action_level1 = menu.addAction(self.tr("Edit object/container"))
        elif level == 2:
            action_level2 = menu.addAction(self.tr("Edit object"))

        action = menu.exec_(self.viewport().mapToGlobal(position))
        if action == action_empty:
            print("action_empty...")
        elif action == action_level0:
            print("action_level0...")
        elif action == action_level1:
            print("action_level1...")
        elif action == action_level2:
            print("action_level2...")
