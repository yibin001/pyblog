# -*- coding: UTF-8 -*-
#相关配置信息
import os
debug = 'SERVER_SOFTWARE' not in os.environ

if debug:
    MYSQL_DB = 'pyblog'
    MYSQL_USER = 'root'
    MYSQL_PASS = ''
    MYSQL_HOST_M = '127.0.0.1'
    MYSQL_HOST_S = '127.0.0.1'
    MYSQL_PORT = '3306'
else:
    import sae.const
    MYSQL_DB = sae.const.MYSQL_DB                # 数据库名
    MYSQL_USER = sae.const.MYSQL_USER            # 用户名
    MYSQL_PASS = sae.const.MYSQL_PASS            # 密码
    MYSQL_HOST_M = sae.const.MYSQL_HOST          # 主库域名（可读写）
    MYSQL_HOST_S = sae.const.MYSQL_HOST_S        # 从库域名（只读）
    MYSQL_PORT = sae.const.MYSQL_PORT            # 端口，类型为，请根据框架要求自行转换为int



AUTH_COOKIE_NAME = 'auth'
ENABLE_PAGE_CACHE = True

STORAGE_DOMAIN_NAME = 'attachment'


#静态资源域
STATIC_DOMAIN = 'http://filestore.b0.upaiyun.com/yibin.im'

blogconfig = {
    'title':u'臭蛋',
    'subtitle':u'一个很臭的蛋',
    'pagesize':10,
    'static_domain':STATIC_DOMAIN,
    'site_domain':'http://yibin.im'
}



#SMTP配置

SMTP_HOST = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USER = 'yibin.net@gmail.com'
SMTP_PASS = 'Yi.Apple@2011'
SMTP_ISSSL = True

# smtp配置结束



Akismet_APP_KEY = 'd74e529c1972'