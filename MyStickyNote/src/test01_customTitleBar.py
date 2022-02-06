import sys
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QTextEdit, QLabel, QLineEdit


class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowFlags(Qt.FramelessWindowHint)

        # 수평 바
        hlayout = QHBoxLayout()

        self.textArea = QTextEdit()
        hlayout.addWidget(self.textArea)
        self.textArea.setStyleSheet("QTextEdit {color:white;background-color:#212121;border-radius:+16px;}")
        self.myFont = QFont("맑은 고딕", 12)
        self.textArea.setFont(self.myFont)

        # 수직바
        self.btnLayout = QVBoxLayout()
        self.btnLayout.addWidget(QPushButton("Open"))
        self.btnLayout.addWidget(QPushButton("Setup"))
        self.btnLayout.addWidget(QPushButton("Find"))
        self.setStyleSheet(
            "QPushButton {max-width:200px;"
            "color:#4fc3f7;"
            "background-color:#424242;border:2px solid #4fc3f7;"
            "border-radius:16px;"
            "font-size:35px;"
            "font-weight:bold;}"
            +
            "QPushButton:hover {color:#212121;"
            "background-color:#4fc3f7;}"
            +
            "QPushButton:pressed {color:white;"
            "background-color:#212121;"
            "border-color:white;}")

        self.status = QTextEdit()
        self.status.insertPlainText("Successfully loaded" + "\nOpen a file...")
        self.status.setReadOnly(1)
        self.status.setStyleSheet(
            "QTextEdit {color:white;background-color:#212121;border-radius:+16px;font-size:14px;max-width:200px;}")
        self.btnLayout.addWidget(self.status)

        self.setFixedSize(800, 400)
        self.setWindowTitle("Py app")
        hlayout.addLayout(self.btnLayout)

        # 커스텀 타이틀 바
        custom_titlebar = TitleBar()

        lay = QVBoxLayout(self)
        lay.addWidget(custom_titlebar)
        lay.addLayout(hlayout)

        self.textArea.setPlaceholderText("메모를 작성하세요...")
        self.textArea.setFocus()


class TitleBar(QWidget):
    def __init__(self, parent=None):
        super(TitleBar, self).__init__(parent)

        #------------------------------------------------------------------------------
        # 타이틀
        # ------------------------------------------------------------------------------
        self.title = QLabel("HMemo")
        #self.title.setPlaceholderText("제목을 작성하세요...")
        self.title.setFixedHeight(35)
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("background-color: #212121;color: rgb(187,187,187);")

        self.myFont = QFont("맑은 고딕", 12)
        self.title.setFont(self.myFont)

        self.title.mouseDoubleClickEvent = self.title_mouseDoubleClickEvent  # 추가

        btn_size = 35

        # ------------------------------------------------------------------------------
        # Sticky 버튼
        # ------------------------------------------------------------------------------
        self.btn_sticky = QPushButton("s")
        self.btn_sticky.clicked.connect(self.btn_sticky_clicked)
        self.btn_sticky.setFixedSize(btn_size, btn_size)
        self.btn_sticky.setStyleSheet("background-color: gray;")
        
        # ------------------------------------------------------------------------------
        # 닫기 버튼
        # ------------------------------------------------------------------------------
        self.btn_close = QPushButton("x")
        self.btn_close.clicked.connect(self.btn_close_clicked)
        self.btn_close.setFixedSize(btn_size, btn_size)
        self.btn_close.setStyleSheet("background-color: red;")

        # ------------------------------------------------------------------------------
        # 최소화 버튼
        # ------------------------------------------------------------------------------
        self.btn_min = QPushButton("-")
        self.btn_min.clicked.connect(self.btn_min_clicked)
        self.btn_min.setFixedSize(btn_size, btn_size)
        self.btn_min.setStyleSheet("background-color: gray;")

        # ------------------------------------------------------------------------------
        # 최대화 버튼
        # ------------------------------------------------------------------------------
        self.btn_max = QPushButton("+")
        self.btn_max.clicked.connect(self.btn_max_clicked)
        self.btn_max.setFixedSize(btn_size, btn_size)
        self.btn_max.setStyleSheet("background-color: gray;")



        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)

        lay.addWidget(self.title)

        #lay.addWidget(self.btn_sticky)
        lay.addWidget(self.btn_min)
        lay.addWidget(self.btn_max)
        lay.addWidget(self.btn_close)

        self.pressing = False
        self.dragPosition = QPoint()

    def resizeEvent(self, QResizeEvent):
        super(TitleBar, self).resizeEvent(QResizeEvent)
        self.title.setFixedWidth(self.window().width())

    def mousePressEvent(self, event):
        self.start = event.globalPos()
        self.pressing = True

    def mouseMoveEvent(self, event):
        if self.pressing:
            self.end = event.globalPos()
            delta = self.end - self.start
            self.window().move(self.window().pos() + delta)
            self.start = self.end

    def mouseReleaseEvent(self, QMouseEvent):
        self.pressing = False

    def btn_close_clicked(self):
        self.window().close()

    def btn_max_clicked(self):
        btnText = self.btn_max.text()
        if btnText == "+":
            self.btn_max.setText("ㅁ")
            self.window().showMaximized()
        else:
            self.btn_max.setText("+")
            self.window().showNormal()

    def btn_min_clicked(self):
        self.window().showMinimized()

    def btn_sticky_clicked(self):
        pass

    def title_mouseDoubleClickEvent(self, QMouseEvent):
        self.btn_max_clicked()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("icon.png"))
    app.setStyleSheet("QWidget {background-color:#424242;border-radius:12px;}")
    app.setFont(QFont("Consolas"))
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())