from PyQt5.QtWidgets import QTreeView, QFileSystemModel, QApplication, QMenu, QAbstractItemView
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
# from src import config

class Tree(QTreeView):
    def __init__(self):
        QTreeView.__init__(self)
        model = QFileSystemModel()
        mypath = QDir.currentPath()
        #model.setRootPath(QDir.currentPath())

        model.setRootPath("D:/test")

        self.setModel(model)
        self.setRootIndex(model.index(QDir.currentPath()))
        model.setReadOnly(False)

        self.setSelectionMode(self.SingleSelection)
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)

    def dragEnterEvent(self, event):
        m = event.mimeData()
        if m.hasUrls():
            for url in m.urls():
                if url.isLocalFile():
                    event.accept()
                    return
        event.ignore()

    def dropEvent(self, event):
        if event.source():
            QTreeView.dropEvent(self, event)
        else:
            ix = self.indexAt(event.pos())
            if not self.model().isDir(ix):
                ix = ix.parent()
            pathDir = self.model().filePath(ix)
            m = event.mimeData()
            if m.hasUrls():
                urlLocals = [url for url in m.urls() if url.isLocalFile()]
                accepted = False
                for urlLocal in urlLocals:
                    path = urlLocal.toLocalFile()
                    info = QFileInfo(path)
                    n_path = QDir(pathDir).filePath(info.fileName())
                    o_path = info.absoluteFilePath()
                    if n_path == o_path:
                        continue
                    if info.isDir():
                        QDir().rename(o_path, n_path)
                    else:
                        qfile = QFile(o_path)
                        if QFile(n_path).exists():
                            n_path += "(copy)"
                        qfile.rename(n_path)
                    accepted = True
                if accepted:
                    event.acceptProposedAction()

app = QApplication(sys.argv)
demo = Tree()
demo.show()
app.exec_()