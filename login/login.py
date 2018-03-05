# coding=utf-8
import json
import requests
import time
import re
import random
from damatuWeb.damatuWeb import DamatuApi
from retrying import retry
from settings import user_name,password

class LogIn:
    def __init__(self):
        self.session = requests.session()
        self.session.headers = {
            'Host': 'kyfw.12306.cn',
            'Origin': 'https://kyfw.12306.cn',
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Referer': 'https://kyfw.12306.cn/otn/login/init',
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
        }
        self.init_cookie()

    def init_cookie(self):
        url = "https://kyfw.12306.cn/otn/HttpZF/logdevice?algID=bkPreI3RAL&hashCode=7gvLZEkQoJprtv1gzPATICcl0jkzJN5iFlYT84cAHys&FMQw=1&q4f3=zh-CN&VPIf=1&custID=133&VEek=unknown&dzuS=0&yD16=0&EOQP=c227b88b01f5c513710d4b9f16a5ce52&lEnu=3232235627&jp76=e237f9703f53d448d77c858b634154a5&hAqN=MacIntel&platform=WEB&ks0Q=b9a555dce60346a48de933b3e16ebd6e&TeRS=877x1440&tOHY=24xx900x1440&Fvje=i1l1o1s1&q5aJ=-8&wNLf=99115dfb07133750ba677d055874de87&0aew=Mozilla/5.0%20(Macintosh;%20Intel%20Mac%20OS%20X%2010_13_2)%20AppleWebKit/537.36%20(KHTML,%20like%20Gecko)%20Chrome/63.0.3239.132%20Safari/537.36&E3gR=adeb286c3dff4be2e738758607d9363b&timestamp={}".format(
            round(time.time() * 1000))
        response = self.session.get(requests.utils.requote_uri(url))
        # print(response.content.decode())
        pattern = re.compile('\(\'(.*?)\'\)')
        userVerify3 = json.loads(pattern.findall(response.content.decode())[0])
        railExpiration = userVerify3['exp']
        railDeviceId = userVerify3['dfp']
        self.session.cookies['RAIL_EXPIRATION'] = railExpiration
        self.session.cookies['RAIL_DEVICEID'] = railDeviceId

    def get_uamtk(self):
        uamtk_url = "https://kyfw.12306.cn/passport/web/auth/uamtk"
        data = {"appid":"otn"}
        response = self.session.post(uamtk_url,data)
        dict_data = json.loads(response.content.decode())
        print("uamtk:{}".format(dict_data["result_message"]))
        if dict_data["result_code"] == 0:
            return dict_data["newapptk"]

    @retry(stop_max_attempt_number = 3)
    def identify_captcha(self):
        captcha_url = 'https://kyfw.12306.cn/passport/captcha/captcha-image?login_site=E&module=login&rand=sjrand&%s' % random.random()
        time.sleep(2)
        response = self.session.get(captcha_url)
        with open("a.png","wb") as f:
            f.write(response.content)
        captcha_code = DamatuApi().decode_by_content(response.content,287)
        print("验证码是:",captcha_code)
        if isinstance(captcha_code,int):
            raise ValueError("余额不足，请检查")
        captcha_code = captcha_code.replace('|', ',')
        if len(captcha_code.split(","))==8 or captcha_code== "ERROR":
            raise ValueError("验证码错误")
        return captcha_code

    @retry(stop_max_attempt_number=5)
    def captcha_check(self):
        captcha_code = self.identify_captcha()
        captcha_check_url = "https://kyfw.12306.cn/passport/captcha/captcha-check"
        data = {
            "answer":captcha_code,
            "login_site":"E",
            "rand":"sjrand"
        }
        resposne = self.session.post(captcha_check_url,data=data)
        ret = json.loads(resposne.content.decode())
        print("captcha_check:{}".format(ret["result_message"]))
        if ret["result_code"] !="4":
                raise ValueError(ret["result_message"])

    def login(self):
        login_url = "https://kyfw.12306.cn/passport/web/login"
        post_data = {
            "username":user_name,
            "password":password,
            "appid":"otn"
        }
        response = self.session.post(login_url,data=post_data)
        dict_ret = json.loads(response.content.decode())
        print("login:{}".format(dict_ret["result_message"]))
        self.session.cookies['uamtk'] = dict_ret['uamtk']  #获取uamtk
        return dict_ret['uamtk']

    def set_uamauthclient(self,newapptk):
        print(newapptk,"~"*10)
        url = "https://kyfw.12306.cn/otn/uamauthclient"
        data = {
            "tk":newapptk
        }
        response = self.session.post(url,data=data)
        dict_ret = json.loads(response.content.decode())
        print("uamauthclient：{}".format(dict_ret["result_message"]))
        if "username" in dict_ret:
            print("用户名是:{}".format(dict_ret["username"]))


    def get_session(self):
        self.get_uamtk() #获取uamtk
        self.captcha_check() #验证验证码
        self.login() #登录
        newapptk = self.get_uamtk()  #获取新的apptk
        self.set_uamauthclient(newapptk) #uamauthclient验证


if __name__ == '__main__':
    train = LogIn()
    train.get_session()

