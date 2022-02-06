#웹 브라우저
import sys
from PyQt5.Qt import *
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QLineEdit
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import QSize, QUrl
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWebEngineWidgets import QWebEnginePage, QWebEngineView


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle('catafest browser')

        self.browser_toolbar = QToolBar()
        self.addToolBar(self.browser_toolbar)
        self.back_button = QPushButton()
        # self.back_button.setIcon(QIcon('left.png'))
        self.back_button.clicked.connect(self.back_page)
        self.browser_toolbar.addWidget(self.back_button)
        self.forward_button = QPushButton()
        # self.forward_button.setIcon(QIcon('right.png'))
        self.forward_button.clicked.connect(self.forward_page)
        self.browser_toolbar.addWidget(self.forward_button)

        self.web_address = QLineEdit()
        self.web_address.returnPressed.connect(self.load_page)
        self.browser_toolbar.addWidget(self.web_address)

        self.web_browser = QWebEngineView()
        self.setCentralWidget(self.web_browser)
        first_url = "https://pypi.org/project/PyQt5/"

        self.web_address.setText(first_url)
        self.web_browser.load(QUrl(first_url))
        self.web_browser.page().titleChanged.connect(self.setWindowTitle)
        self.web_browser.page().urlChanged.connect(self.changed_page)

    def load_page(self):
        url = QUrl.fromUserInput(self.web_address.text())
        if url.isValid():
            self.web_browser.load(url)

    def back_page(self):
        self.web_browser.page().triggerAction(QWebEnginePage.Back)

    def forward_page(self):
        self.web_browser.page().triggerAction(QWebEnginePage.Forward)

    def changed_page(self, url):
        self.web_address.setText(url.toString())


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWin = MainWindow()
    availableGeometry = app.desktop().availableGeometry(mainWin)
    mainWin.resize(availableGeometry.width(), availableGeometry.height())
    mainWin.show()
    sys.exit(app.exec_())