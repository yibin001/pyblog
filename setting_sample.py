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
ENABLE_PAGE_CACHE = True


# sae storage 名
STORAGE_DOMAIN_NAME = '<your_sae_storage_domain_name>'        


#静态资源域,结尾不要加/，比如：http://xxxx.com/static
STATIC_DOMAIN =  '<your_static_file_domain>'    

blogconfig = {
    'title':u'a simple blog',
    'subtitle':u'',
    'pagesize':10,
    'static_domain':STATIC_DOMAIN,
    'site_domain':''
}



#SMTP配置，用于找回密码

SMTP_HOST = '<SMTP_HOST>'
SMTP_PORT = 0
SMTP_USER = '<SMTP_USER>'
SMTP_PASS = '<SMTP_PASS>'
SMTP_ISSSL = False

# smtp配置结束


# Akismet_APP_KEY设置，用于鉴定垃圾评论
# 可以在这里注册，并获取自己的appkey https://akismet.com/plans/
Akismet_APP_KEY = '<your_Akismet_APP_KEY>'