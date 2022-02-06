import sys
from PyQt5.QtCore import Qt, QModelIndex, QDir
from PyQt5.QtWidgets import QApplication, QTreeView, QMainWindow, QFileSystemModel, QAbstractItemView


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Instance variables
        self.my_view = QTreeView()
        self.my_model = QFileSystemModel()

        # Init FS model to show all computer drives
        model_root_path = str(self.my_model.myComputer())
        self.my_model.setRootPath(model_root_path)

        # Init tree view
        self.my_view.setModel(self.my_model)
        self.my_view.setRootIndex(self.my_model.index(model_root_path))
        self.my_view.setSelectionMode(QAbstractItemView.SingleSelection)
        self.my_view.setSelectionBehavior(QAbstractItemView.SelectRows)

        # Connect selection change events to custom slot
        select_model = self.my_view.selectionModel()
        select_model.currentRowChanged.connect(self.current_row_changed)

        # Main window
        self.setCentralWidget(self.my_view)
        self.setGeometry(200, 200, 800, 600)

        # Select initial row on view
        focus_path = QDir.currentPath()
        focus_index = self.my_model.index(focus_path)
        self.my_view.setCurrentIndex(focus_index)

    def current_row_changed(self):
        """Current row of the model has changed"""

        # Scroll view to new row
        index = self.my_view.selectionModel().currentIndex()
        self.my_view.scrollTo(index, QAbstractItemView.EnsureVisible)
        self.my_view.resizeColumnToContents(0)

        # Show path of current row in window title
        absolute_path = self.my_model.filePath(index)
        self.setWindowTitle(absolute_path)


def main():
    a = QApplication(sys.argv)
    mw = MyWindow()
    mw.show()
    sys.exit(a.exec_())

if __name__ == '__main__':
    main()