"""
https://groups.google.com/d/msg/python_inside_maya/1EzNG_i9Xes/Au-18UaXAwAJ
Capturing the start and end item/index information in a
PySide2 QTreeWidget internal drag and drop
"""
from __future__ import print_function

from PyQt5 import QtCore, QtGui, QtWidgets


class Window(QtWidgets.QMainWindow):

    def __init__(self):
        super(Window, self).__init__()
        self._tree = tree = QtWidgets.QTreeWidget()
        tree.setDragDropMode(tree.InternalMove)
        self.setCentralWidget(tree)
        self.__dragged = None

        for i in range(3):
            item = QtWidgets.QTreeWidgetItem(['item{}'.format(i)])
            for j in range(3):
                item.addChild(QtWidgets.QTreeWidgetItem(['child{}-{}'.format(i, j)]))
            tree.addTopLevelItem(item)

        tree.expandAll()
        tree.dropMimeData = self._dropMimeData
        tree.viewport().installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == event.DragEnter:
            # TODO: handle multi-selection?
            item = self._tree.selectedItems()[0]
            idx = self._tree.indexFromItem(item)
            self.__dragged = item
            print('drag:', item.text(0), ', row:', idx.row())

        elif event.type() == event.Drop:
            parent_item = self._tree.itemAt(event.pos())
            parent_idx = self._tree.indexFromItem(parent_item)

            child_item, self.__dragged = self.__dragged, None

            print('drop')
            print('  parent:', parent_item.text(0), ', row:', parent_idx.row())

            self._tree.dropEvent(event)

            child_idx = self._tree.indexFromItem(child_item)
            print('  child:', child_item.text(0), ', row:', child_idx.row())

            return True

        return False


app = QtWidgets.QApplication([])
win = Window()
win.resize(800, 600)
win.show()
app.exec_()