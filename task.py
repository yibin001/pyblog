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


class Redis(tornado.web.RequestHandler):
    def get(self):
        import requests

        try:
            r = requests.get('http://pass.hujiang.com/signup/monitor/redis.aspx', timeout=4.0)
            if r.text != '0':
                self._SMSWarning(r.text)
        except Exception, e:
            self._SMSWarning(str(e))
        self.write('Success')


    def _SMSWarning(self, body,sendmail = True):
        import  urllib
        body = urllib.urlencode(body)
        url = 'http://api.smsbao.com/sms?u=yibin&p=4287fcc7a0e75d7d7d9fecab57926849&m=18668035738&c={0}'.format(body)
        import requests
        try:
            r = requests.get(url)
        except Exception,e:
            pass
        import common
        common.sendmail('yibin.net@qq.com',u'pass redis crash','''
        pass redis crash< br />
        response is {0}
        '''.format(body))


urls = [
    (r"/task/?", Sync),
    (r'/redis/?', Redis),
]
