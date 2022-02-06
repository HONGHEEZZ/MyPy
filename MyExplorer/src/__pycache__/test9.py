from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import *


class MyTest(QWidget):
    """
        ContextMenuPolicy --> ActionsContextMenu
    """

    def __init__(self):
        super().__init__()
        vbox = QVBoxLayout()

        table = QTableWidget(self)
        table.setColumnCount(3)
        table.setRowCount(2)

        table.setContextMenuPolicy(Qt.ActionsContextMenu)

        copy_action = QAction("복사하기", table)
        quit_action = QAction("Quit", table)

        table.addAction(copy_action)
        table.addAction(quit_action)

        copy_action.triggered.connect(self.__copy)
        quit_action.triggered.connect(qApp.quit)

        # table.show()
        vbox.addWidget(table)
        self.setLayout(vbox)
        self.resize(300, 200)

    @pyqtSlot()
    def __copy(self):
        print("복사...")


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    ex = MyTest()
    ex.show()
    sys.exit(app.exec_())
