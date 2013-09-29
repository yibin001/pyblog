# -*- coding: UTF-8 -*-
#相关配置信息
import os

debug = 'SERVER_SOFTWARE' not in os.environ

if debug:
    MYSQL_DB = 'pyblog'                          # 数据库名
    MYSQL_USER = ''                              # 用户名
    MYSQL_PASS = ''                              # 密码
    MYSQL_HOST_M = '127.0.0.1'                   # 主库域名（可读写）
    MYSQL_HOST_S = '127.0.0.1'                   # 从库域名（只读）
    MYSQL_PORT = '3306'                          # 端口，类型为，请根据框架要求自行转换为int
else:
    import sae.const

    MYSQL_DB = sae.const.MYSQL_DB                # 数据库名
    MYSQL_USER = sae.const.MYSQL_USER            # 用户名
    MYSQL_PASS = sae.const.MYSQL_PASS            # 密码
    MYSQL_HOST_M = sae.const.MYSQL_HOST          # 主库域名（可读写）
    MYSQL_HOST_S = sae.const.MYSQL_HOST_S        # 从库域名（只读）
    MYSQL_PORT = sae.const.MYSQL_PORT            # 端口，类型为，请根据框架要求自行转换为int
AUTH_COOKIE_NAME = 'auth'
ENABLE_PAGE_CACHE = False
# sae storage 名
STORAGE_DOMAIN_NAME = '<your bucket name>'

#是否启用qiniu一键加速镜象
enable_qiniu_speed = True

#qiniu域名，结尾不要加/
qiniu_speed_url = '<your qiniu url>'

#静态资源域,结尾不要加/，比如：http://xxxx.com/static
STATIC_DOMAIN = '<your static domain>'

blogconfig = {
    'title': u'a simple blog',
    'subtitle': u'',
    'pagesize': 10,
    'static_domain': STATIC_DOMAIN,
    'site_domain': '<your blog url eg:http://yibinim.sinaapp.com>'
}



#SMTP配置，用于找回密码

SMTP_HOST = '<your smtp host>'
SMTP_PORT = 587
SMTP_USER = '<your smtp username>'
SMTP_PASS = '<your smtp password>'
SMTP_ISSSL = True

# smtp配置结束

# Akismet_APP_KEY设置，用于鉴定垃圾评论
# 可以在这里注册，并获取自己的appkey https://akismet.com/plans/
Akismet_APP_KEY = '<your skismet app key>'