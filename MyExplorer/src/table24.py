# simply use
#your_widget.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

# Example :
import sys
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout

app = QApplication(sys.argv)

window = QWidget()
window.setGeometry(300, 300, 400, 200)
window.show()

v = QVBoxLayout()
l1 = QLabel("This label now has pointing hand cursor")
l2 = QLabel("but this label has default cursor")
l1.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor)) # set cursor to pointing hand

v.addWidget(l1)
v.addWidget(l2)
window.setLayout(v)

app.exec_()