# coding=utf-8
from login.login import LogIn
import json

class Book
    def __init__(self):
        self.session = LogIn().get_session()

    def check_left_ticks(self):
        url = "https://kyfw.12306.cn/otn/leftTicket/queryZ?leftTicketDTO.train_date=2018-02-15&leftTicketDTO.from_station=BJP&leftTicketDTO.to_station=CDW&purpose_codes=ADULT"
        response = self.session.get(url)



