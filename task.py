#!/usr/bin/env python
# -*- coding: UTF-8 -*-



import os, time, math
import tornado.web

from setting import *
from model import db_master


class Sync(tornado.web.RequestHandler):
    def get(self):
        act = self.get_argument('act', '')
        if act != '':
            if act == 'comment':
                sql = "update py_posts set commentcount = (select count(0) from py_comment where postid=py_posts.id and status = 1 and isspam = 0)"
            elif act == 'tag':
                sql = "update py_tags set postcount = (select count(0) from py_post_tag where tagid=py_tags.id)"
            elif act == 'category':
                sql = "update py_category set postcount = (select count(0) from py_post_category where categoryid=py_category.id)"
            db_master._ensure_connected()
            db_master.execute(sql)
            self.write('Success')
        else:
            self.write('Failed')

def SendSMS(body):
    import urllib
    import common
    body = urllib.quote(body)
    url = 'http://api.smsbao.com/sms?u=yibin&p=4287fcc7a0e75d7d7d9fecab57926849&m=18668035738&c={0}'.format(body)
    import requests
    try:
        r=requests.get(url,timeout=5.0)
    except Exception,e:
        common.error_log('send sms error:{0}'.format(e.message))


class Redis(tornado.web.RequestHandler):
    def get(self):
        import requests
        try:
            r = requests.get('http://pass.hujiang.com/signup/monitor/redis.aspx',timeout = 3.0)
            if r.text != '0':
                SendSMS(u'Redis Warn：{0}'.format(r.text))
        except Exception,e:
            SendSMS(u'Redis error：{0}'.format(e.message))
        self.write('Success')

class hjapi(tornado.web.RequestHandler):
    def get(self):
        import requests
        import json
        try:
            r = requests.get('http://hjapi.hujiang.com/account/?act=loginverify&sign=ed23da697e5fe014fb8802cf803f4ca979776b4f&appkey=9c0b989a7d2d8c5a952475c0f61e792f&account=jason0723&password=04476680b22c4bb8',timeout = 2.0)
            val = json.loads(r.text)
            if int(val['code']) !=0:
                SendSMS(u'hjapi Warn:{0}'.format(r.text))
        except Exception,e:
            SendSMS(u'hjapi error:'+e.message)
        self.write('Sussess')



urls = [
    (r"/task/?", Sync),
    (r'/hjapi/?', hjapi),
    (r'/redis/?',Redis)
]
