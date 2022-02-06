
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QHBoxLayout
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QPoint

class MyCustomTitleBar (QWidget):

    def __init__(self, parent=None):

        super (MyCustomTitleBar, self).__init__(parent)
        self.myParent = parent

        self.setStyleSheet(
            "QPushButton {max-width:20px; min-height:20px"
            "color:#4fc3f7;"
            "background-color:#424242;"
            #"border:2px solid #4fc3f7;"
        
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

        #타이틀
        self.title = QLabel("HMemo")
        self.title.setFixedHeight (20)
        self.title.setAlignment (Qt.AlignCenter)

        #self.title.setStyleSheet (f"max-width: g_screen_with)px; background-color:#212121; color: rgb(187, 187, 187);")
        self.title.setStyleSheet ("background-color: #424242; color: rgb(187, 187, 187);")

        self.myFont = QFont("맑은 고딕", 12)
        self.title.setFont(self.myFont)

        self.title.mouseDoubleClickEvent = self.title_mouseDoubleclickEvent # 추가

        btn_size = 35

        # 최소화 버튼
        self.btn_min = QPushButton("_")
        self.btn_min.clicked.connect(self.btn_min_clicked)
        self.btn_min.setFixedSize(btn_size, btn_size)
        self.btn_min.setStyleSheet("background-color:# 424242;")

        # 최대화 버튼
        self.btn_max = QPushButton("□")
        self.btn_max.clicked.connect(self.btn_max_clicked)
        self.btn_max.setFixedSize(btn_size, btn_size)

        self.btn_max.setStyleSheet("background-color:# 424242;")

        # 닫기 버튼
        self.btn_close = QPushButton("X")
        self.btn_close.clicked.connect(self.btn_close_clicked)
        self.btn_close.setFixedSize(btn_size, btn_size)

        self.btn_close.setStyleSheet("background-color:# 424242;")
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self.title)
        lay.addWidget(self.btn_min)
        lay.addWidget(self.btn_max)
        lay.addWidget(self.btn_close)

        self.pressing = False
        self.dragPosition = QPoint()

    def mousePressEvent(self, event):
        self.start = event.globalPos()
        self.pressing = True

    def mouseMoveEvent(self, event):

        if self.pressing:
            self.end = event.globalPos()
            delta = self.end - self.start
            self.window().move(self.window().pos() + delta)
            self.start = self.end

    def mouseReaseEvent(self, QMouseEvent):
        self.pressing = False

    def resizeEvent(self, ResizeEvent):
        # super (TitleBar, self).resize Event (QResizeEvent)
        # self.title. setFixedwidth (self.window).width())
        pass

    def btn_close_clicked(self):
        # self.window().close()
        self.myParent.close()

    def btn_min_clicked(self):
        self.window().showMinimized()

    def btn_max_clicked(self):

        btnText = self.btn_max.text()

        if btnText == "□":
            self.btn_max.setText("▣")
            self.window().showMaximized()

        else:
            self.btn_max.setText("□")
            self.window().showNormal()

    def title_mouseDoubleclickEvent(self, QMouseEvent):
        self.btn_max_clicked()

