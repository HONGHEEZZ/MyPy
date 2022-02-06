
#https://notstop.co.kr/767/
# -*- coding:utf-8 -*-
import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QTreeView
from PyQt5.Qt import QFileSystemModel
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 600, 300)
        self.setWindowTitle('Test Signal')

        # 전체 파일 경로를 가져온다.
        self.path_root = QtCore.QDir.rootPath()
        self.model = QFileSystemModel()
        #self.model.setRootPath(self.path_root)
        self.model.setRootPath('')

        self.index_root = self.model.index(self.model.rootPath())

        self.tree_view = QTreeView()
        self.tree_view.setModel(self.model)
        self.tree_view.setRootIndex(self.index_root)
        self.tree_view.clicked.connect(self.on_treeView_clicked)

        self.setCentralWidget(self.tree_view)

    @pyqtSlot(QtCore.QModelIndex)
    def on_treeView_clicked(self, index):
        indexItem = self.model.index(index.row(), 0, index.parent())

        fileName = self.model.fileName(indexItem)
        filePath = self.model.filePath(indexItem)

        print(fileName)
        print(filePath)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())