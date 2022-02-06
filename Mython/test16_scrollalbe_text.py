from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys

longText = "\n".join(["{}: long text - auto scrolling ".format(i) for i in range(100)])

class AnimationTextEdit(QTextEdit):
    def __init__(self, *args, **kwargs):
        QTextEdit.__init__(self, *args, **kwargs)
        self.animation = QVariantAnimation(self)
        self.animation.valueChanged.connect(self.moveToLine)

    @pyqtSlot()
    def startAnimation(self):
        self.animation.stop()
        self.animation.setStartValue(0)
        self.animation.setEndValue(self.verticalScrollBar().maximum())
        self.animation.setDuration(self.animation.endValue()*4)
        self.animation.start()

    @pyqtSlot(QVariant)
    def moveToLine(self, i):
        self.verticalScrollBar().setValue(i)

class MyApp(QWidget):
    def __init__(self):
        super(MyApp, self).__init__()
        self.setFixedSize(600, 400)
        self.txt = AnimationTextEdit(self)
        self.btn = QPushButton("Start", self)
        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.txt)
        self.layout.addWidget(self.btn)
        self.txt.append(longText)
        self.txt.moveToLine(0)
        self.btn.clicked.connect(self.txt.startAnimation)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())