import sys
from PyQt5.QtWidgets import QApplication, QFileSystemModel, QDesktopWidget
from PyQt5.QtWidgets import QTreeView, QWidget, QVBoxLayout, QMenu
from PyQt5.QtGui import QIcon
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QObject


#https://python-catalin.blogspot.com/2020/08/python-qt5-get-item-data-from.html
# 컨텍스트 메뉴...

class my_app_tree(QWidget):

    def __init__(self):
        super().__init__()
        self.title = "show files and folders on tree view"
        # self.left = 0
        # self.top = 0
        # self.width = 640
        # self.height = 480
        self.center()
        self.resize(640, 480)
        self.initUI()

    def center(self):
        frame_geometry = self.frameGeometry()
        center_position = QDesktopWidget().availableGeometry().center()
        frame_geometry.moveCenter(center_position)
        self.move(frame_geometry.topLeft())

    def context_menu(self, position):
        menu = QMenu()
        copy_action = menu.addAction("Get folder")
        quit_action = menu.addAction("Quit")
        action = menu.exec_(self.tree.mapToGlobal(position))
        # quit application
        if action == quit_action:
            my_application.quit()
        # copy folder name from item
        elif action == copy_action:
            item = self.tree.selectedIndexes()[0].data()
            print("name folder is: " + str(item))

    def initUI(self):
        self.setWindowTitle(self.title)
        # the next source code line is used with left, top, width, height from __init__
        # self.setGeometry(self.left, self.top, self.width, self.height)

        self.model = QFileSystemModel()
        self.model.setRootPath('')
        self.tree = QTreeView()
        self.tree.setModel(self.model)

        self.tree.setAnimated(False)
        self.tree.setIndentation(20)
        self.tree.setSortingEnabled(True)

        self.tree.setWindowTitle("Dir View")
        self.tree.resize(640, 480)

        windowLayout = QVBoxLayout()
        windowLayout.addWidget(self.tree)
        self.setLayout(windowLayout)

        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.context_menu)

        self.show()


if __name__ == '__main__':
    my_application = QApplication(sys.argv)
    example = my_app_tree()
    sys.exit(my_application.exec_())