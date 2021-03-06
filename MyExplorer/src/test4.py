import sys
from PyQt5.QtWidgets import (QWidget, QGridLayout, QPushButton, QApplication)


class basicWindow(QWidget):
    def __init__(self):
        super().__init__()
        grid_layout = QGridLayout()
        self.setLayout(grid_layout)

        button = QPushButton('1-3')
        grid_layout.addWidget(button, 0, 0, 1, 3)

        button = QPushButton('4, 7')
        grid_layout.addWidget(button, 1, 0, -1, 1)

        for x in range(1, 3):
            for y in range(1, 3):
                button = QPushButton(str(str(3 * x + y)))
                grid_layout.addWidget(button, x, y)

        self.setWindowTitle('Basic Grid Layout')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    windowExample = basicWindow()
    windowExample.show()
    sys.exit(app.exec_())