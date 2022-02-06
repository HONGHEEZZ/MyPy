from PyQt5.QtCore import Qt, QPoint, pyqtSlot
from PyQt5.QtWidgets import *


class MyTest(QWidget):
    """
    ContextMenuPolicy --> CustomContextMenu

    ; QPoint를 매개변수로 사용하는 customContextMenuRequested singal을 사용한다.
    """

    def __init__(self):
        super().__init__()
        vbox = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setRowCount(3)

        self.table.setContextMenuPolicy(Qt.CustomContextMenu)

        self.table.customContextMenuRequested.connect(self.__context_menu)

        vbox.addWidget(self.table)
        self.setLayout(vbox)

    # @pyqtSlot('QPoint')
    @pyqtSlot(QPoint)
    def __context_menu(self, position):
        menu = QMenu()
        copy_action = menu.addAction("복사하기")
        quit_action = menu.addAction("Quit")
        action = menu.exec_(self.table.mapToGlobal(position))
        if action == quit_action:
            qApp.quit()
        elif action == copy_action:
            print("copy...")


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    ex = MyTest()
    ex.show()
    sys.exit(app.exec_())
