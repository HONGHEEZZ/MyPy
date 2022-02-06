import sys
from PyQt5.QtWidgets import *
from src import Kiwoom

import time
from pandas import DataFrame
import datetime

MARKET_KOSPI   = 0
MARKET_KOSDAQ  = 10

class PyMon:
    def __init__(self):
        self.kiwoom = Kiwoom.Kiwoom()
        self.kiwoom.comm_connect()

        self.get_code_list()

    def run(self):
        print("run")
        print(self.kospi_codes[0:4])
        #print(self.kosdaq_codes[0:4])

        # df = self.get_ohlcv('000040', '20210301')
        # print(df)

        buy_list = []
        num = len(self.kospi_codes)
        for i, code in enumerate(self.kospi_codes):
            print(i, '/', num)
            if i >= 99: break
            if self.check_speedy_rising_volume(code):
                name = self.kiwoom.get_master_code_name(code)
                print("급등주:[%s] %s" % (code, name))

                buy_list.append([code, name])

        self.update_buy_list(buy_list)

    #급등주 파일에 기록하기
    def update_buy_list(self, buy_list):
        f = open("../buy_list.txt", "wt")
        for item in buy_list:
            #한주당 얼마냐에 따라 수량을 조절해야 함. LG화학은 1주에 100만원임....
            f.writelines("매수;{};{};시장가;10;0;매수전\n".format(item[0], item[1]))
        f.close()

    #거래량... 급등주 포착 알고리즘
    def check_speedy_rising_volume(self, code):

        #'20210226'과 같은 포맷으로 얻기 위해 datetime 모듈을 사용
        today = datetime.datetime.today().strftime("%Y%m%d")
        df = self.get_ohlcv(code, today)

        #거래량 칼럼만 바인딩....
        volumes = df['volume']


        # 기준 : 과거 20일 거래량. 부족시 종료
        if len(volumes) < 21:
            return False

        sum_vol_20 = 0
        today_vol = 0

        for i, vol in enumerate(volumes):
            if i == 0:
                today_vol = vol
            elif 1 <= i <= 20:
                sum_vol_20 += vol
            else:
                break


        avg_vol_20 = sum_vol_20 / 20

        #* 거래량 10개 증가한 종목 포착....
        #* 거래량 증가 == 주가 상승?????
        if today_vol > avg_vol_20 * 10:
        #if today_vol > avg_vol_20 :
            print("[{}]오늘 거래량:[{}], 20일 평균 거래량 [{}]".format(code, today_vol, avg_vol_20))
            return True





    #과거 거래일별 시가, 고가, 저가, 종가, 거래량 가져오기
    def get_ohlcv(self, code, start):
        self.kiwoom.ohlcv = {'date' : [], 'open' : [], 'high' : [], 'low' : [], 'close' : [], 'volume' : [] }

        self.kiwoom.set_input_value("종목코드", code)
        self.kiwoom.set_input_value("기준일자", start)
        self.kiwoom.set_input_value("수정주가구분", 1)

        #TR을 한 번 요청하면 과거 900일에 대한 데이터 받을 수 있음.
        self.kiwoom.comm_rq_data("opt10081_req", "opt10081", 0, "0101")
        time.sleep(0.2)


        df = DataFrame(self.kiwoom.ohlcv, columns = ['open', 'high', 'low', 'close', 'volume'],
                       index=self.kiwoom.ohlcv['date'])

        return df


    # 코드 가져오기
    def get_code_list(self):
        self.kospi_codes = self.kiwoom.get_code_list_by_market(MARKET_KOSPI)
        #self.kosdaq_codes = self.kiwoom.get_code_list_by_market(MARKET_KOSDAQ)



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
    pymon = PyMon()
    pymon.run()