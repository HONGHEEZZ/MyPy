import sys

from PyQt5.QtCore import QDir
from PyQt5.QtWidgets import QFileSystemModel, QTreeView, QWidget, QHBoxLayout, QApplication

#https://alwaysemmyhopes.com/ko/python/679296-difference-between-setrootpath-and-setrootindex-in-qfilesystemmodel-python-python-3x-pyqt-pyqt5-qfilesystemmodel.html
if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = QWidget()
    lay = QHBoxLayout(w)
    model = QFileSystemModel()
    model.setRootPath(QDir.rootPath())
    for dirname in (QDir.rootPath(), QDir.homePath(), QDir.currentPath()):
        view = QTreeView()
        view.setModel(model)
        view.setRootIndex(model.index(dirname))
        lay.addWidget(view)
        w.show()

    sys.exit(app.exec_())