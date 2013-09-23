#!/usr/bin/env python
# -*- coding: UTF-8 -*-


import tornado
import os,time,math,json
from common import BaseHandler,render,client_cache,Authentication,cache_page,isint,isemail,spam_check,get_location_byip
from setting import *
from model import Category,Tag,Post,Comment,BlogUser

class Logout(BaseHandler):
    def get(self):
        self.set_secure_cookie(AUTH_COOKIE_NAME,'',expires_days=-1)
        self.redirect('/')

class Feed(BaseHandler):
    @cache_page(expire_time=3600)
    def get(self):
        count,data = Post.get_post(page=1,pagesize=15)
        self.datamap['rss']  = data
        self.set_header('Content-Type', 'application/xml;charset=utf-8') 
        
        self.write(render.rss(self.datamap))
        
        

class HomePage(BaseHandler):
    #@client_cache(600, 'public')
    @cache_page(expire_time=300)
    def get(self,page=1):
        page = int(page)
        count,data = 0,None
        key = self.get_argument('s','')
        if key:
            key = key.replace("'","\'")
            self.datamap['key'] = key
            count,data = Post.search_post_by_title(key)
        else:
            count,data = Post.get_post(page=page,pagesize=blogconfig['pagesize'])
        
        self.datamap['recent'] = Post.get_recent_post()
        self.datamap['count'] = count
        self.datamap['data']  = data
        
        self.datamap['page'] = int(page)
        self.datamap['pageurl'] = 'page'
        self.datamap['pagecount'] = int(math.ceil(float(count)/blogconfig['pagesize']))
        self.write(render.blog_index(self.datamap))

class PostPage(BaseHandler):
    @cache_page(expire_time=120)
    def get(self,id):
        post = None

        act = self.get_argument('act','')
        if act == 'del_comment' and self.islogin:
            cid = self.get_argument('cid',0)
            Comment.delete_comment_by_id(cid)
            
            self.add_header('content-type','application/json;charset=utf-8')
            self.write(json.dumps({'code':0,'msg':'OK'}))
            return


        if isint(id):
            post = Post.get_post_by_id(id,ignorestatus=True)
        else:
            post = Post.get_post_by_alias(id,ignorestatus=True)
        
        if not post or post.status !=0 :
            self.set_error(404)
        act = self.get_argument('act','')
        if act=='clear':
            self.set_secure_cookie('post_'+str(id),'',expires_days=-10)
        self.datamap['valid'] = True
        if post.password.strip() !="":
            if self.get_secure_cookie('post_'+str(id)) !=post.password:
                self.datamap['valid'] = False
        if act and self.islogin:
            if act == 'delete':
                Post.delete_post_by_id(id)
                self.redirect('/')
                return
            elif act=='edit':
                self.redirect('/admin/?url=/admin/post/edit/%s/' % post.id)
                return
        self.datamap['post'] = post
        self.datamap['recent'] = Post.get_recent_post()
        comment = Comment.get_comments_by_postid(post.id,isAdmin = self.islogin)
        self.datamap['commentcount'] = comment[0]
        self.datamap['comments'] = comment[1]
        if self.islogin:
            self.datamap['curr_user_info'] = self.get_current_user_info
        self.write(render.post(self.datamap))
    def post(self,id):
        post = Post.get_post_by_id(id)
        if not post:
            self.set_error(404)
        if post.password.strip()!="":
            password = self.get_argument('password','')
            if password == post.password:
                self.set_secure_cookie('post_'+str(id),password,expires_days=1)
            else:
                self.flash(u'验证密码不正确')
        self.redirect('/post/'+str(id)+'/')


class PostComment(BaseHandler):
    def get(self):
        self.set_error(400)
    def post(self,id):

        post = Post.get_post_by_id(id)
        if not post or post.status !=0 or post.commentstatus == 1:
            self.write('抱歉，评论功能已关闭。')
        else:
            username = self.get_argument('username','')
            email    = self.get_argument('email','')
            content  = self.get_argument('comment','')
            parentid = int(self.get_argument('parentid',0))
            if self.islogin:
                curr_user_info = self.get_current_user_info
                username = curr_user_info.username
                email    = curr_user_info.email
            
            if username =='' or content == or not isemail(email)'':
                self.flash(u'错误:称呼、电子邮件与内容是必填项')
                self.redirect(post.url)
                return
            username = username[:20]
            content = content[:512]
            if not self.islogin:
                is_spam = spam_check(content,self.request.remote_ip)
            else:
                is_spam = 0
            location = get_location_byip(self.request.remote_ip)
            Comment.post_comment(postid=id,username=username,email=email,content=content,parentid=parentid,ip=self.request.remote_ip,isspam=is_spam,location=location)
            if is_spam:
                self.flash(u'您的评论可能会被认定为Spam')
            self.set_comment_user(username,email)
            self.redirect(post.url)

class CategoryPage(BaseHandler):
    @cache_page(expire_time=120)
    def get(self,category,page=1):
        page = int(page)
        category = category[:-1]
        count,data = Post.get_post(page=page,pagesize=blogconfig['pagesize'],category=category)
      
        self.datamap['recent'] = Post.get_recent_post()
        self.datamap['count'] = count
        self.datamap['data']  = data
        self.datamap['pageurl'] = 'category'
        self.datamap['page'] = page
        self.datamap['pagecount'] = int(math.ceil(float(count)/blogconfig['pagesize']))
        self.write(render.blog_index(self.datamap))

class TagPage(BaseHandler):
    @cache_page(expire_time=120)
    def get(self,tag,page=1):
        page = int(page)
        tag = tag[:-1]
        count,data = Post.get_post(page=page,pagesize=blogconfig['pagesize'],tag=tag)
        
        self.datamap['recent'] = Post.get_recent_post()
        self.datamap['count'] = count
        self.datamap['data']  = data
        self.datamap['pageurl'] = 'tag'
        self.datamap['page'] = page
        self.datamap['pagecount'] = int(math.ceil(float(count)/blogconfig['pagesize']))
        self.write(render.blog_index(self.datamap))


class Page(BaseHandler):
    @cache_page(expire_time=120)
    def get(self,alias):
        self.write(alias)

class ForgotPassword(BaseHandler):
    def get(self):
        self.write(render.forgotpassword(self.datamap))
    def post(self):
        import common
        username = self.get_argument('username','')
        if not username:
            self.flash(u'请输入用户名')
            self.redirect('')
        else:
            user = BlogUser.get_user_by_username(username)
            if not user:
                self.flash(u'用户名不存在')
                self.redirect('')
            else:
                kvdata = {"user":username,"email":user.email}
                key = common.md5(common.randomstr(20))
                common.set_kvdb_value(key,kvdata)
                url = 'http://%s/reset/%s/' % (self.request.host,key)
                common.sendmail(user.email,u'重置密码',url)
                self.flash(u'邮件发送成功')
                self.redirect('')


class ResetPassword(BaseHandler):
    def get(self,key):
        import common
        value = common.get_kvdb_value(key)
        if not value:
            self.write(u'对不起，token已失效')
            
            return
        self.datamap['_name'] = value['user']
        self.write(render.resetpassword(self.datamap))
    def post(self,key):
        import common
        value = common.get_kvdb_value(key)
        if not value:
            self.write(u'对不起，token已失效')
            return
        password = self.get_argument('password','')
        confirm =  self.get_argument('confirmpassword','')
        if not password or not confirm:
            self.flash(u'密码不能为空')
            self.redirect('')
            return
        if password !=confirm:
            self.flash(u'二次输入的密码不一致')
            self.redirect('')
            return
        BlogUser.update_user(value['user'],value['email'],common.md5(password))
        common.delete_kvdb(key)
        self.set_secure_cookie(AUTH_COOKIE_NAME,'',expires_days=-7)
        self.write(u'密码重置成功')
        

class PageNotFoundHandler(BaseHandler):
    def get(self):
        raise tornado.web.HTTPError(404)

class Test(BaseHandler):
    def get(self):
        
        self.write(render.test(self.datamap))
    def post(self):
        self.flash(time.strftime('%H:%M:%S', time.localtime()))
        self.redirect('')



urls = [
    (r"/", HomePage),
    (r"/feed/?", Feed),
    (r"/p/(\d+)/?", HomePage),
    (r"/post/(\w+)/?", PostPage),
    (r"/page/(\w+)/?", PostPage),
    (r"/category/(\S+)/?", CategoryPage),
    (r"/category/(\S+)/p/(\d+)/?", CategoryPage),
    (r"/tag/(\S+)/?", TagPage),
    (r"/tag/(\S+)/(\d+)/?", TagPage),
    (r"/logout/?", Logout),
    (r"/postcomment/(\d+)/?", PostComment),
    (r"/forgotpassword/?", ForgotPassword),
    (r"/reset/([0-9a-zA-Z]{32})/?", ResetPassword),
    (r"/test/",Test),
    
    
]
