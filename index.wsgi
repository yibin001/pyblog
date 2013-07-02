import sae
import tornado.wsgi,tornado
from common import BaseHandler
from blog import PageNotFoundHandler
from blog import urls as blogurls
from admin import urls as adminurls
from task import urls as taskurls
settings = { 
    'debug': False,
    'gzip': True,
    'cookie_secret':"61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
    "xsrf_cookies": False
}

tornado.web.ErrorHandler = PageNotFoundHandler


error_url = [(r".*",PageNotFoundHandler)]
app = tornado.wsgi.WSGIApplication(blogurls+adminurls+taskurls+error_url, **settings)

application = sae.create_wsgi_app(app)