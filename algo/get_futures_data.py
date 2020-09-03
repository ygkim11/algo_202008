import os
import sys
import csv

from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from config.errorCode import *
from PyQt5.QtTest import *
from config.kiwoomType import *



class Get_futures_data(QAxWidget):
    def __init__(self):
        super().__init__()

        print(5*"#" + "Kiwoom initiated" + 5*"#")

        #event_loop
        self.event_loop = QEventLoop()

        #screen_num
        self.screen_calculation_stock = "4000"


        self.daily_data = []

        #실행
        self.get_ocx_instance()
        self.event_slots()
        self.signal_login_commConnect()

        # self.calculator_fnc()
        self.db_prac()


    def get_ocx_instance(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")


    def signal_login_commConnect(self):
        self.dynamicCall("CommConnect()")

        self.event_loop.exec_()

    def login_slot(self, errCode):
        print(errors(errCode))
        self.event_loop.exit()

    def event_slots(self):
        self.OnEventConnect.connect(self.login_slot)
        self.OnReceiveTrData.connect(self.trdata_slot)


    ###TR 데이터 분봉####
    def trdata_slot(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext):
        '''
        TR요청 받는 함수
        :param sScrNo: 스크린번호
        :param sRQName: 요청 이름(내가 지정)
        :param sTrCode: 요청ID, TR코드
        :param sRecordName: 사용안함
        :param sPrevNext: 다음페이지가 있는지
        :return:
        '''

        if sRQName == "선옵일자별체결요청":

            code = self.dynamicCall("GetCommData(Qstring, Qstring, int, Qstring)", sTrCode, sRQName, 0, "종목코드")
            code = code.strip()
            code = "005930"
            print("%s 일봉데이터 요청" % code)

            cnt = self.dynamicCall("GetRepeatCnt(Qstring, Qstring)", sTrCode, sRQName)
            print("조회되는 데이터 일수 : %s" % cnt)

            # data =self.dynamicCall("GetCommDataEx(Qstring, Qstring)", sTrcode, sRQName)
            # 600개씩 한번에 줌...아래의 형태로!
            #[['', '현재가', '거래량', '거래대금','날짜','시가','고가','저가',''],['', '현재가', '거래량', '거래대금','날짜','시가','고가','저가','']]


            for i in range(cnt):
                data = []

                current_price = self.dynamicCall("GetCommData(Qstring, Qstring, int, Qstring)", sTrCode, sRQName, i, "현재가n")
                date = self.dynamicCall("GetCommData(Qstring, Qstring, int, Qstring)", sTrCode, sRQName, i, "체결일자")

                # data.append("")
                data.append(date.strip())
                data.append(current_price.strip())
                # data.append("")

                self.daily_data.append(data.copy())


            print(self.daily_data)
            print(len(self.daily_data))


            if sPrevNext == "2": #2로 바꾸면 과거데이터 계속 업데이트 시킴
                self.day_kiwoom_db(code=code, sPrevNext=sPrevNext)

            else:
                f = open(r"C:/Users/YG/PycharmProjects/algo_202008/db/"+code+"_futures.csv", "a", newline="", encoding="utf8")


                with f:
                    self.header = [['date', 'current']]
                    write = csv.writer(f)
                    write.writerows(self.header)
                    write.writerows(self.daily_data)

                f.close()

                self.daily_data.clear()
                print("saved!!!!!!!!!!!!")

                self.event_loop.exit()


    def get_code_list_by_market(self, market_code):
        '''
        종목코드 반환  (개발가이드 > 기타함수> 종목정보관련함수)
        :param market_code:
        :return:
        '''
        code_list = self.dynamicCall("GetCodeListByMarket(QString)", market_code)
        code_list = code_list.split(";")[:-1]

        return code_list


    def day_kiwoom_db(self, code=None, date=None, sPrevNext="0"):

        QTest.qWait(3600)

        self.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        # self.dynamicCall("SetInputValue(QString, QString)", "수정주가구분", "1")
        #
        # if date != None:
        #     self.dynamicCall("SetInputValue(QString, QString)", "기준일자", date)

        self.dynamicCall("CommRqData(QString, QString, int, QString)", "선옵일자별체결요청", "opt50002", sPrevNext, self.screen_calculation_stock)

        self.event_loop.exec_()


    def calculator_fnc(self):
        '''
        종목분석 실행용
        :return:
        '''
        code_list = self.get_code_list_by_market("10") #10:코스닥
        print(code_list)

        print("코스닥 갯수 %s" % len(code_list))

        for idx, code in enumerate(code_list):

            #screen 번호 꽉찰까바 방지용 ( 꼭 안써도된다)
            self.dynamicCall("DisconnectRealData(QString)", self.screen_calculation_stock)

            print("%s /%s : KOSDAQ Stock Code: %s is Updating..." % (idx+1, len(code_list),code))

            self.day_kiwoom_db(code=code)


    def db_prac(self):
        self.day_kiwoom_db(code="005930")
        # code_list = self.get_code_list_by_market("0")


