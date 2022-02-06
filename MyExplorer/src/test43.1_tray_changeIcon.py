import sys
from PyQt5.QtWidgets import QSystemTrayIcon, QApplication, QMenu
from PyQt5.QtGui import QIcon

class autoparse():
    def __init__(self):

       self.main()

    def main(self):
        app = QApplication(sys.argv)

        self.trayIcon = QSystemTrayIcon(QIcon("../ico/shell32_dll_280_folder.ico"), app)
        self.menu = QMenu()
        self.autopconfig = self.menu.addAction('Config')
        self.autopconfig.triggered.connect(self.swapicon)
        self.trayIcon.setContextMenu(self.menu)

        self.trayIcon.show()
        sys.exit(app.exec_())
    def swapicon(self):
        self.trayIcon.setIcon(QIcon("../ico/shell32_dll_42_tree.ico"))

test1 = autoparse()