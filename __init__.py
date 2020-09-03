from algo.get_daily_data import *
from algo.get_minute_data import *
from algo.get_futures_data import *
from algo.get_data import *

from PyQt5.QtWidgets import *
import sys

class Main():
    def __init__(self):

        print(5*"#" + "Main initiated" + 5*"#")

        self.app = QApplication(sys.argv)

        # self.get_futures_data = Get_futures_data()
        # self.get_daily_data = Get_daily_data()
        # self.get_minute_data = Get_minute_data()
        self.get_data = Get_data(_data_kind= "daily")

        self.app.exec_()


if __name__ == '__main__':
    Main()
