# -*- coding: utf-8 -*-
"""
@author: catafest
"""
import sys
import sys, os
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QAction, qApp, QApplication, QDesktopWidget
from PyQt5.QtWidgets import QMenu, QPlainTextEdit, QSizePolicy
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QSize


#텍스트 에디터...
#https://python-catalin.blogspot.com/search/label/PyQt5
class Example(QMainWindow):
    # init the example class to draw the window application
    def __init__(self, parent=None):
        super(Example, self).__init__(parent)
        size_policy = self.sizePolicy()
        size_policy.setHeightForWidth(True)
        size_policy.setVerticalPolicy(QSizePolicy.Preferred)
        self.setSizePolicy(size_policy)
        self.initUI()

    # create the def center to select the center of the screen
    def center(self):
        # geometry of the main window
        qr = self.frameGeometry()

        # center point of screen
        cp = QDesktopWidget().availableGeometry().center()
        # move rectangle's center point to screen's center point
        qr.moveCenter(cp)
        # top left of rectangle becomes top left of window centering it
        self.move(qr.topLeft())

    # create the init UI to draw the application
    def initUI(self):
        # create the action for the exit application with shortcut and icon
        # you can add new action for File menu and any actions you need
        # self.setMinimumSize(QSize(440, 240))
        self.setWindowTitle("parse sensors output - catafest")
        self.editor_text = QPlainTextEdit(self)
        # font
        default_font = self.editor_text.font()
        default_font.setPointSize(9)
        self.editor_text.setFont(default_font)

        self.setCentralWidget(self.editor_text)
        # self.editor_text.setMinimumSize(400,600)

        self.editor_text.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.editor_text.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)

        self.editor_text.setObjectName("editor_text")
        self.editor_text.setEnabled(True)

        openAct = QAction(QIcon('open.png'), '&Open', self)
        openAct.setShortcut('Ctrl+O')
        openAct.setStatusTip('Open file')
        openAct.triggered.connect(self.my_OpenDialog)

        exitAct = QAction(QIcon('exit.png'), '&Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(qApp.quit)
        # create the status bar for menu
        self.statusBar()
        # create the menu with the text File , add the exit action
        # you can add many items on menu with actions for each item
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        # create open
        fileMenu.addAction(openAct)
        # create exit
        fileMenu.addAction(exitAct)

        # add submenu to menu
        submenu = QMenu('Submenu', self)

        # some dummy actions
        submenu.addAction('Submenu 1')
        submenu.addAction('Submenu 2')

        # allow adding a sphere
        meshMenu = submenu.addMenu('Mesh')
        self.add_sphere_action = QAction('Add Sphere', self)
        self.add_sphere_action.triggered.connect(self.add_sphere)
        meshMenu.addAction(self.add_sphere_action)

        # add to the top menu
        menubar.addMenu(submenu)

        # layout = QtWidgets.QGridLayout(self)
        # layout.addWidget(self.editor_text)
        self.editor_text

        # resize the window application
        self.resize(960, 720)
        # draw on center of the screen
        self.center()
        # add title on windows application
        self.setWindowTitle('Simple menu')
        # show the application
        self.show()
        # close the UI class

    def my_OpenDialog(self):
        path = QtWidgets.QFileDialog.getOpenFileName(
            self, 'Open file', '',
            'Text files (*.txt);;HTML files (*.html)')[0]
        if path:
            file = QtCore.QFile(path)
            if file.open(QtCore.QIODevice.ReadOnly):
                stream = QtCore.QTextStream(file)
                text = stream.readAll()
                info = QtCore.QFileInfo(path)
                if info.completeSuffix() == 'txt':
                    # self.editor_text.setHtml(text)
                    self.editor_text.insertPlainText(text)
                else:
                    self.editor_text.setPlainText(text)
                file.close()

    def add_sphere(self):
        """ add text with sphere """
        print("sphere")


if __name__ == '__main__':
    # create the application
    app = QApplication(sys.argv)
    # use the UI with new  class
    ex = Example()
    # run the UI
    sys.exit(app.exec_())