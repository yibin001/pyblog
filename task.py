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



urls = [
    (r"/task/?", Sync),
]
