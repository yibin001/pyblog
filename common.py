# -*- coding: UTF-8 -*-
import os,re,string,random,re
from hashlib import md5 as hashmd5
import tornado.web
import torndb
import inspect

from functools import partial
from jinja2 import Environment, PackageLoader
from extensions import flash_message
import time
import json
from setting import *
import templatefilter
try:
    import pylibmc
    cache = pylibmc.Client()
except:
    import memcache
    cache = memcache.Client(['localhost:11211'], debug=True)

######## mail相关
if not debug:
    import sae.mail

def sendmail(to,subject,body):
    sae.mail.send_mail(to, subject, body,
        (SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, SMTP_ISSSL))


######## kvdb相关
if not debug:
    import sae.kvdb

def get_kvdb_value(key):
    if debug:return None
    kv = sae.kvdb.KVClient()
    
    return kv.get(str(key))

def set_kvdb_value(key,value):
    if debug:return
    kv = sae.kvdb.KVClient()
    kv.set(str(key),value)

def delete_kvdb(key):
    if debug:return True
    kv = sae.kvdb.KVClient()
    return kv.delete(str(key))

######## end


def randomstr(length,stringtype = 0):
    val = None
    if stringtype == 0:
        val = string.ascii_letters
    elif stringtype == 1:
        val = string.digits
    elif stringtype == 2:
        val = string.ascii_letters+string.digits
    return ''.join(random.sample(val,length))



def md5(val):
    return hashmd5(val).hexdigest()


class render_jinja:
    """Rendering interface to Jinja2 Templates
    Example:

        render= render_jinja('templates')
        render.hello(name='jinja2')
    """
    def __init__(self, *a, **kwargs):
        extensions = kwargs.pop('extensions', [])
        globals = kwargs.pop('globals', {})
        globals['date'] = int(time.time())
        from jinja2 import Environment,FileSystemLoader
        self._lookup = Environment(loader=FileSystemLoader(*a, **kwargs), extensions=extensions,trim_blocks=True)
        self._lookup.globals.update(globals)
        
    def __getattr__(self, name):
       
        path = name + '.html'
        t = self._lookup.get_template(path)
        return t.render


def isemail(value):
    return re.match("\w+([-+.']\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*",value)

def ispassword(value):
    return re.match("^[a-zA-Z0-9]{1}([a-zA-Z0-9]|[._~!@#$%^&*()]){4,14}$",value)

def isusername(value):
    return re.match("^[a-zA-Z]{1}([a-zA-Z0-9]|[._]){4,14}$",value)

def isint(value):
    return re.match("^\d+$",value)


myFilters = {'int2time'     : templatefilter.int2time,
                 'mail2avatar'  : templatefilter.mail2avatar,

               
                 'date_gmt'     : templatefilter.date_gmt,
                 
                 'formattime'   : templatefilter.formattime,
                 'html'         : templatefilter.html,
                 'avatar'       : templatefilter.globalavatar,
                }

def Render(theme='',filepath='',isAdmin=False):
    template = os.path.join(os.path.dirname(__file__) + '/templates' + ('/default' if theme=='' else "/"+theme))
    if isAdmin:
        template = os.path.join(os.path.dirname(__file__) + '/templates/admin')
    if filepath:
        template = os.path.join(template,filepath)
    render = render_jinja(
        template,
        encoding = 'utf-8',
    )
    render._lookup.filters.update(myFilters)
    return render

render = Render('default')
render_admin = Render(theme='default',isAdmin = True)

def deleteCache(key):
    cache.delete(key)

def FlushCache():
    cache.flush_all()

def SetCache(key,value,expire=3600):
    val =  cache.add(str(key),value,time = expire)


def GetCache(key):
    key = str(key)
    return cache.get(key)

def error_log(error_info):
    import logging
    logging.error(error_info)


def cacheData(key_pattern, expire=120):
    def deco(f):
        arg_names, varargs, varkw, defaults = inspect.getargspec(f)
        if varargs or varkw:
            raise Exception("not support varargs")
        def _(*a, **kw):
            param = dict(zip(arg_names,a))
            key = key_pattern
            
            if isinstance(param,object) and defaults :
                
                try:
                    _key = arg_names[1:]
                    _values = a[1:]+defaults
                    param = dict(zip(_key,_values))
                except Exception,e:
                    error_log('genrate key is error %s,%s' % (key_pattern,e))
                

            for k,v in param.items():
                key = key.replace('{'+str(k)+'}',str(v))
            for k,v in kw.items():
                key = key.replace('{'+str(k)+'}',str(v))

            val = cache.get(key)
            if val is None:
               
                val = f(*a, **kw)
                if val is None:
                    pass
                else:
                    cache.add(key,val,time = expire)
                   
            else:
                #print '%s is cached...' % key
                pass                
            return val
        return _
    return deco


def client_cache(seconds, privacy=None):
    def wrap(handler):
        def cache_handler(self, *args, **kw):
            self.set_cache(seconds, privacy)
            return handler(self, *args, **kw)
        return cache_handler
    return wrap



def cache_page(key="",expire_time=3600):
    def _decorate(method):
        def _wrapper(*args, **kwargs):
            if not ENABLE_PAGE_CACHE:
                method(*args, **kwargs)
                return
            request=args[0].request
            skey=key+ request.path
            error_log('mc get key:'+skey)
            html= cache.get(skey)

            if html:
                error_log('mc get key '+skey+' OK,length is '+str(len(html)))
                cachetime,html = html

                request.set_header('Cache-Control', 'public,max-age=' % (expire_time))
                request.set_header('Expires','%s' % (time.strftime('%a, %d %b %Y %H:%M:%S GMT',time.gmtime(tiem.time()+expire_time))))
                request.write(html)
            else:
                error_log('mc get key '+skey+' is not found')
                result = method(*args, **kwargs)
                #result = (int(time.time()),result)
                cache.set(skey,result,expire_time)
        return _wrapper
    return _decorate


def get_location_byip(ip):
    '''根据ip获取地区,取自新浪接口'''
    import httplib,json
    path='/iplookup/iplookup.php?format=json&ip=%s' % ip
    connection = httplib.HTTPConnection('int.dpool.sina.com.cn', 80)
    connection.request("POST", path)
    response = connection.getresponse()
    if response.status == 200:
        try:
            jsonstring = json.loads(response.read())
            
            if jsonstring['ret'] == 1:
                return '%s%s%s%s' % (jsonstring['country'],jsonstring['province'],jsonstring['city'],jsonstring['isp'])
        except Exception,e:
            error_log('get_location_byip error:%s' % e)
            pass
    return None

def spam_check(content,ip):
    import akismet
    akismet.USERAGENT = "yibinim/1.0"
    my_api_key = Akismet_APP_KEY
    content = content.encode('utf-8')
    spam = False
    print 'spam_check(%s) : %s' % (ip,content)
    try:
        real_key = akismet.verify_key(my_api_key,blogconfig['site_domain'])
        print 'real_key is %s' % real_key
        if real_key:
            is_spam = akismet.comment_check(my_api_key,blogconfig['site_domain'],ip, "Mozilla/5.0 (...) Gecko/20051111 Firefox/1.5", comment_content=content)
            print 'is_spam is %s ' % is_spam
            spam = is_spam
    except akismet.AkismetError, e:
        print 'akismet error : %s,%s' % ( e.response, e.statuscode)
    return spam


def Authentication(url='/admin/login/'):
    def wrap(handler):
        def authorized_handler(self, *args, **kw):
            request = self.request
            user = self.get_current_user
            if request.method == 'GET':
                if not user:
                    self.redirect(url)
                    return False
                else:
                    handler(self, *args, **kw)
            else:
                if not user:
                    self.error(403)
                else:
                    handler(self, *args, **kw)
        return authorized_handler
    return wrap

class BaseHandler(tornado.web.RequestHandler,flash_message.FlashMessage):
    def initialize(self):
        
        global blogconfig
        from model import BlogConfig,Tag,Category,Post,BlogUser
        self.set_header('Content-Type','text/html;charset=utf-8')


        self.datamap ={} # (globals.items())+(locals+items())
        blogconfig.update(BlogConfig.get_configs())
        blogconfig['pagesize'] = int(blogconfig['pagesize'])
        self.blogconfig =  blogconfig
        self.datamap['hot_tag'] = Tag.get_hot_tag(10)
        #self.datamap['categorys'] = Category.get_categorys()
        self.datamap['config'] = blogconfig
        self.datamap['request'] = self.request
        self.datamap['handler'] = self
        self.datamap['time'] = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
        self.datamap['requesttime'] = round(self.request.request_time()*1000,4)
        self.datamap['curr_user'] = self.get_current_user
        self.datamap['comment_user'] = self.get_comment_user
        self.datamap['all_pages'] = Post.get_pages()
        

    def set_comment_user(self,username,email):
        value = json.dumps({'username':username,'email':email})
        self.set_secure_cookie('comment_user', value,httponly=True,expires_days=180)

    

    @property
    def get_comment_user(self):
        value = self.get_secure_cookie('comment_user')
        if value:
            value = json.loads(value)
            return value
        return {'username':'','email':''}

    @property
    def db(self):
        return torndb.Connection(MYSQL_HOST_M+':'+MYSQL_PORT,MYSQL_DB,user=MYSQL_USER,password=MYSQL_PASS,time_zone='+8:00')
    
    def set_error(self,statuscode=400):
        raise tornado.web.HTTPError(statuscode)

    @property
    def islogin(self):
        return self.get_current_user is not None

    @property
    def get_current_user(self):
        return self.get_secure_cookie(AUTH_COOKIE_NAME)

    def finish(self, chunk=None):
        super(BaseHandler, self).finish(chunk)
        try:
            import model
            model.db_master.close()
            model.db_slave.close()
        except Exception,e:
            print 'close db error %s' % e
        finally:
            pass

    def write_error(self, status_code, **kwargs):
        if status_code == 404:
            self.write(render.error_404(self.datamap))
        elif status_code == 500:
            error_log('500 error......')
            self.write(render.error_500(self.datamap))
        else:
            self.write("error:%s" % status_code)
    

    @property
    def get_current_user_info(self):
        from model import BlogUser
        return BlogUser.get_user_by_username(self.get_current_user)

    def set_cache(self, seconds, is_privacy=None):
        if seconds <= 0:
            self.set_header('Cache-Control', 'no-cache')
        else:
            if is_privacy:
                privacy = 'public, '
            elif is_privacy is None:
                privacy = ''
            else:
                privacy = 'private, '
            self.set_header('Cache-Control', '%smax-age=%s' % (privacy, seconds))

