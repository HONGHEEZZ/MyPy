import sys
import os

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class ContentFileSystemModel(QFileSystemModel):

    def __init__(self):
        super(ContentFileSystemModel, self).__init__()

    def supportedDragActions(self) -> Qt.DropActions:
        print("supportedDragActions")
        return Qt.MoveAction | super(ContentFileSystemModel, self).supportedDragActions() | Qt.CopyAction

    def supportedDropActions(self) -> Qt.DropActions:
        print("supportedDropActions")
        return Qt.MoveAction | super(ContentFileSystemModel, self).supportedDropActions() | Qt.CopyAction

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        defaultFlags = super(ContentFileSystemModel, self).flags(index)
        if not index.isValid():
            return defaultFlags
        fileInfo = self.fileInfo(index)
        if fileInfo.isDir():
            return Qt.ItemIsDropEnabled | Qt.ItemIsDragEnabled | defaultFlags
        elif fileInfo.isFile():
            # files should *not* be drop enabled
            return Qt.ItemIsDragEnabled | defaultFlags
        return defaultFlags

    def canDropMimeData(self, data: QMimeData, action: Qt.DropAction,
                        row: int, column: int, parent: QModelIndex) -> bool:
        if row < 0 and column < 0:
            target = self.fileInfo(parent)
        else:
            target = self.fileInfo(self.index(row, column, parent))
        return target.isDir() and target.isWritable()

    def dropMimeData(self, data: QMimeData, action: Qt.DropAction,
                         row: int, column: int, parent: QModelIndex) -> bool:
            if row < 0 and column < 0:
                targetDir = QDir(self.fileInfo(parent).absoluteFilePath())
            else:
                targetDir = QDir(self.fileInfo(self.index(row, column, parent)).absoluteFilePath())
            dataList = []
            # first check if the source is writable (so that we can move it)
            # and that it doesn't already exist on the target path
            for url in data.text().splitlines():
                path = QUrl(url).toLocalFile()
                fileObject = QFile(path)
                if not fileObject.permissions() & QFile.WriteUser:
                    return False
                targetPath = targetDir.absoluteFilePath(QFileInfo(path).fileName())
                if targetDir.exists(targetPath):
                    return False
                dataList.append((fileObject, targetPath))
            # actually move the objects, you might want to add some feedback
            # if movement failed (eg, no space left) and eventually undo the
            # whole operation
            for fileObject, targetPath in dataList:
                if not fileObject.rename(targetPath):
                    return False
            return True

class FileView(QListView):
    def dragMoveEvent(self, event):
        # accept drag movements only if the target supports drops
        if self.model().flags(self.indexAt(event.pos())) & Qt.ItemIsDropEnabled:
            super().dragMoveEvent(event)
        else:
            event.ignore()


def main(argv):
    app = QApplication(sys.argv)

    #path = "C:\\Users\\Me\\Desktop"
    path = "d:\\test"
    file_system_model = ContentFileSystemModel()
    file_system_model.setRootPath(path)
    file_system_model.setReadOnly(False)
    lv_file_manager = FileView()
    #lv_file_manager = QListView()
    lv_file_manager.setModel(file_system_model)
    lv_file_manager.setViewMode(QListView.IconMode)
    lv_file_manager.setRootIndex(file_system_model.index(path))
    lv_file_manager.setResizeMode(QListView.Adjust)

    lv_file_manager.setMovement(QListView.Static)
    lv_file_manager.setSelectionMode(QAbstractItemView.ExtendedSelection)
    lv_file_manager.setWrapping(True)
    lv_file_manager.setAcceptDrops(True)
    lv_file_manager.setDragEnabled(True)
    lv_file_manager.setDropIndicatorShown(True)
    lv_file_manager.setUniformItemSizes(True)
    lv_file_manager.setDragDropMode(QAbstractItemView.InternalMove)
    lv_file_manager.setFlow(QListView.LeftToRight)

    lv_file_manager.show()
    app.exec_()


if __name__ == "__main__":
    main(sys.argv)