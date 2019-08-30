import os
import time
import execjs
import pymongo
import difflib
import requests

from datetime import datetime
from config import *


class CrawlGuaHao(object):
    """
    模拟登录114yygh网站，从本地mongodb:department获取肾内科科室link，
    提取医生挂号信息，存入outpatient集合
    """

    def __init__(self):
        self.client = pymongo.MongoClient(MONGO_URL, MONGO_PORT)
        self.db = self.client[MONGO_DB]
        self.departments = self.db['departments']  # 读取科室url

        self.outpatient = self.db['outpatient']  # 存处医生挂号信息

        self.login_url = 'http://www.114yygh.com/web/login/verify.htm'
        self.post_url = 'http://www.114yygh.com/web/login/doLogin.htm'
        # requests.adapters.DEFAULT_RETRIES = 5
        self.session = requests.Session()
        self.session.adapters.DEFAULT_RETRIES = 5
        # self.session.keep_alive = False
        self.headers = {
            'Host': 'www.114yygh.com',
            'Origin': 'http://www.114yygh.com',
            'Proxy-Connection': 'keep-alive',
            'Referer': 'http://www.114yygh.com/web/login/step.htm',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        }

    def password(self):
        """
        给密码 加密
        :return: 加密字符串str
        """
        with open(os.path.dirname(__file__) + '/sha1.js', encoding='utf-8') as f:
            strs = f.read()
        ctx = execjs.compile(strs).call('hex_sha1', os.getenv('PASSWORD'))
        return ctx

    def login(self):
        post_data = {
            'mobileNo': os.getenv('PHONE'),
            'password': os.getenv('PASSWD'),
            'loginType': 'PASSWORD_LOGIN',
            'redirectUrl': '/index.htm'
        }
        response = self.session.post(self.post_url, headers=self.headers, data=post_data)
        if response.status_code == 200:
            print('Login Successfully!', end=',')
            print(response.text)
        else:
            print('Login Failed!')

    def get_data(self, url, **kwargs):
        try:
            response = self.session.post(url, data=kwargs)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print('get_data:', repr(e), url)

    def parse_registed_info(self, *args, **kwargs):
        """
        解析挂号信息
        :param kwargs: hospitalid, departmentid, dutydate
        :return:
        """
        url = 'http://www.114yygh.com/dpt/build/duty.htm'
        json = self.get_data(url, **kwargs)
        time.sleep(0.4)  # 等待网页加载
        try:
            data = json.get('data')
            for value in data.values():
                for i in value:
                    ratio = difflib.SequenceMatcher(None, i['doctorName'], i['doctorTitleName']).quick_ratio()
                    if ratio < 0.4 and (i['doctorName'] not in '医生普通号肾内科主治医师肾性高血压门诊'):
                        yield {
                            'doctorName': i['doctorName'],
                            'doctorTitleName': i['doctorTitleName'],
                            'skill': i['skill'],
                            'dutyDate': ' '.join([kwargs['dutyDate'], args[0], i['dutyCodeName']]),
                            'totalFee': i['totalFee'],
                            'remainAvailableNumber': [{'remain': i['remainAvailableNumber'],
                                                       'getTime': datetime.now().strftime('%Y-%m-%d %H:%M')}],
                            'hospId': '-'.join([kwargs['hospitalId'], kwargs['departmentId']])
                        }
                    # else:
                    #     print(i['doctorName'], i['doctorTitleName'])
        except Exception as e:
            print('registered_info:', repr(e), json)
            self.session.keep_alive = False
            time.sleep(3)  # 休息一下
            self.login()
            self.parse_registed_info(*args, **kwargs)

    def parse_index_info(self, **kwargs):
        """
        解析挂号索引页信息
        :param kwargs: hostpitalid, departmentid, week
        :return:
        """
        url = 'http://www.114yygh.com/dpt/week/calendar.htm'
        week = 1
        while True:
            json = self.get_data(url, week=week, **kwargs)
            time.sleep(0.4)  # 等待网页加载
            try:
                for item in json['dutyCalendars']:
                    if item.get('remainAvailableNumber') != -1:
                        date = item.get('dutyDate')
                        dutyWeek = '周' + item.get('dutyWeek')
                        results = self.parse_registed_info(dutyWeek, dutyDate=date, **kwargs)
                        for result in results:
                            # print(result)
                            self.save_to_mongo(result)  # 数据保存到MongoDB中

                lastweek = json['lastWeek']
                week = json['week']
                if week < lastweek:
                    week += 1
                else:
                    break
            except Exception as e:
                print('index:', repr(e), json)
                time.sleep(1)
                self.parse_index_info(**kwargs)

    def save_to_mongo(self, result):
        query = {'doctorName': result['doctorName'], 'dutyDate': result['dutyDate']}
        if self.outpatient.find_one(query):
            self.outpatient.update_one({'doctorName': result['doctorName'], 'dutyDate': result['dutyDate'],
                                        'remainAvailableNumber.remain': {"$ne": 0}},  # 数组所有remain都不为0
                                       {'$push': {'remainAvailableNumber': result['remainAvailableNumber'][0]}})
            print(result['remainAvailableNumber'])
        else:
            self.outpatient.insert_one(result)
            print(result)

    def main(self):
        self.login()
        for item in self.departments.find({}, no_cursor_timeout=True):
            link = item.get('link')
            print(link)
            Id = link.replace('.htm', '').split('/')[-1].split('-')  # 提取医院和科室的id
            self.parse_index_info(hospitalId=Id[0], departmentId=Id[1])
        print("\n====================================================\n")


if __name__ == '__main__':
    crawler = CrawlGuaHao()
    # crawler.login()
    crawler.main()
