import sys
import os
from PyQt5 import QtCore
from PyQt5.Qt import *

#https://programmersought.com/article/88805508058/

class MainWidget(QWidget):

    def __init__(self, parent=None):
        super(MainWidget, self).__init__(parent)

        # Get all files in the system
        self.model01 = QFileSystemModel()
        # Filter to display only folders, not files and featured files
        self.model01.setFilter(QtCore.QDir.Dirs | QtCore.QDir.NoDotAndDotDot)
        self.model01.setRootPath('')

        # Define to create the left window
        self.treeView1 = QTreeView(self)
        self.treeView1.setModel(self.model01)
        for col in range(1, 4):
            self.treeView1.setColumnHidden(col, True)
        self.treeView1.doubleClicked.connect(self.initUI)

        # Define to create the right window
        self.model02 = QStandardItemModel()
        self.treeView2 = QTreeView(self)
        self.treeView2.setModel(self.model02)

        # Add the created window
        self.layout = QHBoxLayout()
        self.layout.addWidget(self.treeView1)
        self.layout.addWidget(self.treeView2)
        self.setLayout(self.layout)

    def initUI(self, Qmodelidx):
        # Each click to clear the data in the right window
        self.model02.clear()
        # Define an array of all files under the storage path
        PathData = []
        # Get the specified path after double clicking
        filePath = self.model01.filePath(Qmodelidx)
        # List window file assignment
        PathDataName = self.model02.invisibleRootItem()
        # Get all the files in the folder
        PathDataSet = os.listdir(filePath)
        # Proceed to sort the obtained data
        PathDataSet.sort()
        # Traverse to determine whether the file obtained is a folder or a file, Flase is a file, and True is a folder
        for Data in range(len(PathDataSet)):
            if os.path.isdir(filePath + '\\' + PathDataSet[Data]) == False:
                PathData.append(PathDataSet[Data])
            elif os.path.isdir(filePath + '\\' + PathDataSet[Data]) == True:
                print('2')
                # Put all the obtained files into the array for assignment in the right window.
        for got in range(len(PathData)):
            gosData = QStandardItem(PathData[got])
            PathDataName.setChild(got, gosData)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWidget()
    window.resize(600, 400)
    window.show()
    sys.exit(app.exec_())