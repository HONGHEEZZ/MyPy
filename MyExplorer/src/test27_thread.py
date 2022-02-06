import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class Worker(QThread):
    sig_caller = pyqtSignal(int)   #사용자 정의 시그널

    def __init__(self):
        super().__init__()
        self.num = 0        #초기값 설정

    def run(self):

        while True:
            self.sig_caller.emit(self.num)     #방출

            self.num += 1
            self.sleep(1)

class MyWindow(QMainWindow):
    def __init__(self):

        super().__init__()

        self.worker = Worker()
        self.worker.start()
        self.worker.sig_caller.connect(self.sig_receiver) #시그널 슬롯 등록

        self.edit = QLineEdit(self)
        self.edit.move(10,10)

    @pyqtSlot(int)
    def sig_receiver(self, num):
        self.edit.setText(str(num))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mywindow = MyWindow()
    mywindow.show()
    app.exec_()
