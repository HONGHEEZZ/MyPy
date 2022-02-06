from PyQt5.QtWidgets import (QApplication,QSplitter,QFileSystemModel,
                               QTreeView, QListView, QTableView)
from PyQt5.QtCore import QDir
import sys

if __name__ == '__main__':
    app = QApplication(sys.argv)

    splitter = QSplitter()

    model = QFileSystemModel(app)
    model.setRootPath(QDir.currentPath())

    treeView = QTreeView(splitter)
    treeView.setModel(model)
    treeView.setRootIndex(model.index(QDir.currentPath()))

    listView = QListView(splitter)
    listView.setModel(model)
    listView.setRootIndex(model.index(QDir.currentPath()))

    tableView = QTableView(splitter)
    tableView.setModel(model)
    tableView.setRootIndex(model.index(QDir.currentPath()))

    splitter.setWindowTitle("Three views onto the same file system model")
    splitter.show()
    app.exec_()