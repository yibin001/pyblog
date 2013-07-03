# -*- coding: UTF-8 -*-

import os.path
import re

import tornado.httpserver
import tornado.ioloop
import tornado.web
import unicodedata
from blog import urls as blogurls
from admin import urls as adminurls
settings = { 
    'debug': True,
    'cookie_secret':"61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo="
}
def main():
    
    application = tornado.web.Application(blogurls+adminurls, **settings)
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8888)
    tornado.ioloop.IOLoop.instance().start()


class A():
    __name='a'
    def test(self):
        print self.__name


if __name__ == '__main__':
   
    main()