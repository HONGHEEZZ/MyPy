from PyQt5 import uic

from src.Kiwoom import *

form_class = uic.loadUiType("ui/pytrader.ui")[0]

class MyWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        #자동 매매
        self.trade_stocks_done = False

        self.kiwoom = Kiwoom()
        self.kiwoom.comm_connect()

        self.timer = QTimer(self)
        self.timer.start(1000)
        self.timer.timeout.connect(self.timeout)

        # Timer2 자동조회
        self.timer2 = QTimer(self)
        self.timer2.start(1000 * 10)
        self.timer2.timeout.connect(self.timeout2)

        #종목명 가져오기
        self.lineEdit.textChanged.connect(self.code_changed)

        self.lineEdit.setText("004410")   #서울식품

        #계좌 정보 가져오기
        accounts_num = int(self.kiwoom.get_login_info("ACCOUNT_CNT"))
        accounts = self.kiwoom.get_login_info("ACCNO")

        #accounts = "56243804"   #실계좌... #모의계좌 : 8154579411

        accounts_list = accounts.split(';')[0:accounts_num]
        self.comboBox.addItems(accounts_list)

        #현금 주문
        self.pushButton.clicked.connect(self.send_order)

        #계좌 현행 조회
        self.pushButton_2.clicked.connect(self.check_balance)

        #자동매수/매도 파일 로드
        self.load_buy_sell_list()

    #자동 거래
    def trade_stocks(self):
        hoga_lookup = {'지정가':"00", '시장가':"03"}

        f = open("../buy_list.txt", "rt")
        buy_list = f.readlines()
        f.close()

        f = open("../sell_list.txt", "rt")
        sell_list = f.readlines()
        f.close()

        account = self.comboBox.currentText()

        #buy list
        for row_data  in buy_list:
            split_row_data = row_data.split(';')
            hoga = split_row_data[3]
            code = split_row_data[1]
            name = split_row_data[2]
            num  = split_row_data[4]
            price  = split_row_data[5]

            if split_row_data[-1].rstrip() == '매수전':
                self.statusbar.showMessage("{}({}) 자동매수 주문중....".format(name, code))
                self.kiwoom.send_order("send_order_req", "0101", account, 1,
                                       code, num, price, hoga_lookup[hoga], "")

        # sell list
        for row_data in sell_list:
            split_row_data = row_data.split(';')
            hoga = split_row_data[3]
            code = split_row_data[1]
            name = split_row_data[2]
            num = split_row_data[4]
            price = split_row_data[5]

            if split_row_data[-1].rstrip() == '매도전':
                self.statusbar.showMessage("{}({}) 자동매도 주문중....".format(name, code))
                self.kiwoom.send_order("send_order_req", "0101", account, 2,
                                       code, num, price, hoga_lookup[hoga], "")
                
                
        #매수전/매도전 -> 주문완료
        #변경된 파일 업데이트
        
        #buy list
        for i, row_data in enumerate(buy_list):
            buy_list[i] =buy_list[i].replace("매수전", "주문완료")

        # file update
        f = open("../buy_list.txt", 'wt')
        for row_data in buy_list:
            f.write(row_data)

        f.close()

        # sell list
        for i, row_data in enumerate(sell_list):
            buy_list[i] = buy_list[i].replace("매도전", "주문완료")

        # file update
        f = open("../sell_list.txt", 'wt')
        for row_data in buy_list:
            f.write(row_data)

        f.close()

    #자동매수/매도 파일 로드
    def load_buy_sell_list(self):
        f = open("../buy_list.txt", 'rt')
        buy_list=f.readlines()
        f.close()

        f = open("../sell_list.txt", 'rt')
        sell_list = f.readlines()
        f.close()

        row_count = len(buy_list) + len(sell_list)
        self.tableWidget_4.setRowCount(row_count)

        #buy list
        for j in range(len(buy_list)):
            row_data = buy_list[j]
            split_row_data = row_data.split(';')
            # 파일에 종목명도 추가되어 있음.
            #split_row_data[1]=self.kiwoom.get_master_code_name(split_row_data[1].rsplit())

            for i in range(len(split_row_data)):
                item = QTableWidgetItem(split_row_data[i].rstrip())
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignCenter)

                # row, col
                self.tableWidget_4.setItem(j, i, item)

        # sell list
        for j in range(len(sell_list)):
            row_data = sell_list[j]
            split_row_data = row_data.split(';')
            # 파일에 종목명도 추가되어 있음.
            #split_row_data[1] = self.kiwoom.get_master_code_name(split_row_data[1].rstrip())

            for i in range(len(split_row_data)):
                item = QTableWidgetItem(split_row_data[i].rstrip())
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignCenter)
                self.tableWidget_4.setItem(len(buy_list) + j, i, item)

        self.tableWidget_4.resizeRowsToContents()



    #자동조회
    def timeout2(self):
        if self.checkBox.isChecked():
            self.check_balance()


    # 계좌 현행 조회
    def check_balance(self):
        self.kiwoom.reset_opw00018_output()
        account_number = self.kiwoom.get_login_info("ACCNO")
        account_number = account_number.split(';')[0]

        self.kiwoom.set_input_value("계좌번호", account_number)
        self.kiwoom.comm_rq_data("opw00018_req", "opw00018", 0, "2000")

        while self.kiwoom.remained_data:
            time.sleep(0.2)
            self.kiwoom.set_input_value("계좌번호", account_number)
            self.kiwoom.comm_rq_data("opw00018_req", "opw00018", 2, "2000")

        # opw00001
        self.kiwoom.set_input_value("계좌번호", account_number)
        self.kiwoom.comm_rq_data("opw00001_req", "opw00001", 0, "2000")

        # balance
        item = QTableWidgetItem(self.kiwoom.d2_deposit)
        item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
        self.tableWidget.setItem(0, 0, item)

        for i in range(1, 6):
            item = QTableWidgetItem(self.kiwoom.opw00018_output['single'][i - 1])
            item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
            self.tableWidget.setItem(0, i, item)

        self.tableWidget.resizeRowsToContents()

        # Item list
        item_count = len(self.kiwoom.opw00018_output['multi'])
        self.tableWidget_2.setRowCount(item_count)

        for j in range(item_count):
            row = self.kiwoom.opw00018_output['multi'][j]
            for i in range(len(row)):
                item = QTableWidgetItem(row[i])
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
                self.tableWidget_2.setItem(j, i, item)

        self.tableWidget_2.resizeRowsToContents()


    # 현금 주문
    def send_order(self):
        order_type_lookup = {'신규매수':1, '신규매도':2, '매수취소':3, '매도취소':4}
        hoga_lookup = {'지정가':"00", '시장가':"03"}

        account = self.comboBox.currentText()
        order_type = self.comboBox_2.currentText()
        code = self.lineEdit.text()
        hoga = self.comboBox_3.currentText()
        num = self.spinBox.value()
        price = self.spinBox_2.value()

        print("send order 직전...")
        self.kiwoom.send_order("send_order_req", "0101",
                               account, order_type_lookup[order_type], code, num,
                               price, hoga_lookup[hoga], "")

        print("send order 직후...")


    def code_changed(self):
        code = self.lineEdit.text()
        name = self.kiwoom.get_master_code_name(code)
        self.lineEdit_2.setText(name)


    def timeout(self):
        market_start_time = QTime(9,0,0)

        current_time = QTime.currentTime()


        #자동 매매
        if current_time > market_start_time and self.trade_stocks_done is False:
            self.trade_stocks()
            self.trade_stocks_done = True

        text_time = current_time.toString("hh:mm:ss")
        time_msg = "현재시간: " + text_time

        state = self.kiwoom.get_connect_state()

        if state == 1:
            state_msg = "서버 연결 중..."
        else:
            state_msg = "서버와 연결 끊김..."

        self.statusbar.showMessage(state_msg + " | " + time_msg)

def my_exception_hook(exctype, value, traceback):
    # Print the error and traceback
    print(exctype, value, traceback)

    # Call the normal Exception hook after
    sys._excepthook(exctype, value, traceback)
    # sys.exit(1)



if __name__ == "__main__":
    # Back up the reference to the exceptionhook
    sys._excepthook = sys.excepthook

    # Set the exception hook to our wrapping function
    sys.excepthook = my_exception_hook



    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()