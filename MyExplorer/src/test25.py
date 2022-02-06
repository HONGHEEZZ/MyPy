from PyQt5 import QtCore, QtGui, QtWidgets
import sys

class Ui_Form(QtWidgets.QWidget):
    def __init__(self, nb_courbes=1, nom_courbes='', parent=None):
        super(Ui_Form, self).__init__(parent)
        self.setupUi(self)

    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(249, 169)
        self.tabWidget = QtWidgets.QTabWidget(Form)
        self.tabWidget.setGeometry(QtCore.QRect(40, 40, 127, 80))
        self.tabWidget.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.tabWidget.addTab(self.tab_2, "")




if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    form = Ui_Form()
    form.show()
    sys.exit(app.exec_())