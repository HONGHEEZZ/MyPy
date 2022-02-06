from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import *




class TableWidget(QTableWidget):
    """
    ContextMenuPolicy --> ActionsContextMenu
    """
    def __init__(self, parent=None):
        QTableWidget.__init__(self, parent)
        self.setColumnCount(3)
        self.setRowCount(3)


        self.setContextMenuPolicy(Qt.ActionsContextMenu)


        copy_action = QAction("복사하기", self)
        quit_action = QAction("Quit", self)


        self.addAction(copy_action)
        self.addAction(quit_action)


        quit_action.triggered.connect(qApp.quit)
        copy_action.triggered.connect(self.__copy)


    @pyqtSlot()
    def __copy(self):
        print("복사...")




if __name__ == "__main__":
    import sys


    app = QApplication([])
    tableWidget = TableWidget()
    tableWidget.show()
    sys.exit(app.exec_())
