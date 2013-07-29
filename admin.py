<<<<<<< HEAD
# -*- coding: UTF-8 -*-
import os,time,math
from common import BaseHandler,render,client_cache,Authentication,render_admin,randomstr
from setting import *
import common
from model import Category,Tag,Post,Comment,BlogConfig,BlogUser
import json
import hashlib
if not debug:
    import sae.mail
    from sae.taskqueue import add_task
    import sae.storage
    



######
def put_obj2storage(file_name = '', data = '', expires='365', type=None, encoding= None, domain_name = STORAGE_DOMAIN_NAME):
    file_name='attachment/'+file_name
    bucket = sae.storage.Bucket(domain_name)
    bucket.put_object(file_name, data, content_type=type, content_encoding=encoding,metadata={"expires":"365d"})
    return bucket.generate_url(file_name)





class Upload(BaseHandler):
    @Authentication()
    def get(self):
        self.write(render_admin.upload(self.datamap))
    def post(self):
        self.set_header('Content-Type','text/html')
        rspd = {'status': 201, 'msg':'ok'}
        callback = self.get_argument('callback','callback');
        filetoupload = self.request.files['filetoupload']
        isimage = 0
        if filetoupload:
            myfile = filetoupload[0]

            
            try:

                file_type = myfile['filename'].split('.')[-1].lower()
                
                isimage = file_type in ['jpg','jpeg','gif','bmp']
                new_file_name = "%s.%s"% (randomstr(10,2), file_type)
                
            except Exception,e:
                print str(e)
                file_type = ''
                new_file_name = randomstr(10,2)
            ##
            mime_type = myfile['content_type']
            encoding = None
            ###
            
            try:
                attachment_url = put_obj2storage(file_name = new_file_name, data = myfile['body'], expires='365', type= mime_type, encoding= encoding)
            except Exception,e:
                print str(e)
                attachment_url = ''
            
            if attachment_url:
                rspd['status'] = 200
                rspd['filename'] = myfile['filename']
                rspd['msg'] = attachment_url
            else:
                rspd['status'] = 500
                rspd['msg'] = 'put_obj2storage erro, try it again.'
        else:
            rspd['msg'] = 'No file uploaded'

        self.write("""
<script type="text/javascript">
    var data = {};
    data.filetype = '%s';
    
    data.url = '%s';
    data.isimage = %d;
    window.parent.uploadCallBack(data);
</script>""" % (file_type, attachment_url,1 if isimage else 0))
        return        

class Login(BaseHandler):
    def get(self):
        self.write(render_admin.login(self.datamap))
    def post(self):
        username = self.get_argument('username','')
        password = self.get_argument('password','')
       
        rememberme = int(self.get_argument('rememberme',1))
        if self.db.get("select * from py_user where username=%s and password=%s limit 1",username,common.md5(password)):
            self.set_secure_cookie(AUTH_COOKIE_NAME,username,httponly=True,expires_days=rememberme)
            self.redirect('/admin/')
        else:
            self.flash(u'用户名与密码不匹配')
            self.redirect('/admin/login/')

class AdminHomePage(BaseHandler):
    @Authentication()
    def get(self):
        self.datamap['url'] = self.get_argument('url','')
        self.write(render_admin.index(self.datamap))
class CommentList(BaseHandler):
    @Authentication()
    def get(self):
        page = int(self.get_argument('page',1))
        if self.get_argument('act','')=='delete':
            Comment.delete_comment_by_id(int(self.get_argument('id',0)))
        pagesize = 20
        rtn = Comment.get_comments(pagesize=pagesize)
        self.datamap['comments'] = rtn[1]
        self.datamap['count'] = rtn[0]
        self.datamap['pagecount'] = int(math.ceil(float(rtn[0])/pagesize))
        self.write(render_admin.comment(self.datamap))


class EditPost(BaseHandler):
    @Authentication()
    def get(self,id):
        post = Post.get_post_by_id(id,ignorestatus=True)
        self.datamap['category'] = Category.get_categorys()
        self.datamap['tags']     = Tag.get_tags()
        
        self.datamap['post'] = post
        

        self.datamap['chose_tag'] = [x.tag for x in post.tag]
        self.datamap['chose_category'] =[x.category for x in post.category] 
        self.write(render_admin.editpost(self.datamap))
    def post(self,id):
        title  =  self.get_argument('title','')
        content = self.get_argument('content','',strip=False)
        status =  self.get_argument('status',0)
        tag = self.get_arguments('tag',[])
        category = self.get_arguments('category',[])
        input_category = self.get_argument('input_category','')
        input_tag = self.get_argument('input_tag','')
        posttype = self.get_argument('posttype',0)
        alias = self.get_argument('alias','')
        tag = list(set(tag+input_tag.split(',')))
        category = list(set(category+input_category.split(',')))
        commentstatus = self.get_argument('commentstatus',0)
        password = self.get_argument('password','')
        
        if title =='' or content=='':
            self.datamap['message'] = u'标题与内容不能为空'
        else:
            rtn = Post.edit_post(id=id,title = title,content = content,status = status,commentstatus = commentstatus,password = password,tag = tag,category = category,posttype=posttype,alias=alias)
            if rtn:
                self.flash(u'修改成功')
            else:
                self.flash(u'修改失败')
            self.redirect('/admin/post/edit/'+id+'/')

class AdminAddPost(BaseHandler):
    @Authentication()
    def get(self):
        self.datamap['category'] = Category.get_categorys()
        self.datamap['tags']     = Tag.get_tags()
        self.write(render_admin.admin_newpost(self.datamap))
        
    @Authentication()
    def post(self):
        title  =  self.get_argument('title','')
        content = self.get_argument('content','',strip=False)
        status =  self.get_argument('status',0)
        tag = self.get_arguments('tag',[])
        category = self.get_arguments('category',[])
        input_category = self.get_argument('input_category','')
        input_tag = self.get_argument('input_tag','')
        posttype = self.get_argument('posttype',0)
        alias = self.get_argument('alias','')
        tag = list(set(tag+input_tag.split(',')))
        category = list(set(category+input_category.split(',')))
        commentstatus = self.get_argument('commentstatus',0)
        password = self.get_argument('password','')
        
        if title =='' or content=='':
            self.datamap['message'] = u'标题与内容不能为空'
        else:
            postid = Post.new_post(title = title,content = content,status = status,commentstatus = commentstatus,password = password,tag = tag,category = category,alias=alias,posttype=posttype)
            if postid:
                self.redirect('/admin/post/')
            else:
                self.write('faild')

class BlogList(BaseHandler):
    @Authentication()
    def get(self):
        page = int(self.get_argument('page','1'))
        key = self.get_argument('key','')
        act = self.get_argument('act','')
        if act=='delete':
            Post.delete_post_by_id(int(self.get_argument('id',0)))
        pagesize = 20
        count,blogs = Post.get_post(page=page,pagesize=pagesize,showall=True,keyword=key,onlypost=False)

        for x in blogs:
            x.length = len(x.content)
        self.datamap['count'] = count
        self.datamap['posts'] = blogs
        self.datamap['page'] = int(page)
        self.datamap['pagecount'] = int(math.ceil(float(count)/pagesize))
        self.write(render_admin.post(self.datamap))

class Left(BaseHandler):
    def get(self):
        self.write(render_admin.left(self.datamap))


class Top(BaseHandler):
    def get(self):
        self.write(render_admin.top(self.datamap))

class Settings(BaseHandler):
    @Authentication()
    def get(self):
        
        self.write(render_admin.settings(self.datamap))
    def post(self):
        title = self.get_argument('title',u'')
        subtitle = self.get_argument('subtitle','')
        pagesize = int(self.get_argument('pagesize',10))
        enablecomment = self.get_argument('enablecomment',1)
        isclose = self.get_argument('isclose',0)
        BlogConfig.update_configs(title=title,subtitle=subtitle,pagesize=pagesize,enablecomment=enablecomment,isclose=isclose)
        self.flash(u'配置更新成功')
        self.redirect('/admin/config/')

class Password(BaseHandler):
    @Authentication()
    def get(self):
        self.datamap['user'] = BlogUser.get_user_by_username(self.get_current_user)
        self.write(render_admin.password(self.datamap))
    @Authentication()
    def post(self):
        password = self.get_argument('password','')
        newpassword = self.get_argument('newpassword','')
        confirmpassword = self.get_argument('confirmpassword','')
        
        user = BlogUser.get_user_by_username(self.get_current_user)
        email = self.get_argument('email',user.email)
        if password and newpassword and newpassword:
            if newpassword == confirmpassword:
                user = self.db.get("select * from py_user where username=%s limit 1",self.get_current_user)
                if user:
                    if user.password == common.md5(password):
                        rowcount = BlogUser.update_user(self.get_current_user,email,common.md5(newpassword))
                        if rowcount == 1:
                            self.set_secure_cookie(AUTH_COOKIE_NAME,'',expires_days=-10)
                            
                            self.flash(u"密码修改成功，请重新登录。")
                        else:
                            self.flash(u"密码保存失败")
                    else:
                        self.flash(u"原密码验证不正确")
            else:
                self.flash(u"二次输入的密码不一致")
        else:
            BlogUser.update_user(self.get_current_user,email,user.password)
        self.redirect('')

urls = [
    (r"/admin/?", AdminHomePage),
    (r"/admin/post/add/?", AdminAddPost),
    (r"/admin/post/edit/(\d+)/?", EditPost),
    (r"/admin/post/?", BlogList),
    (r"/admin/login/?", Login),
    (r"/admin/upload/?",Upload),
    (r"/admin/top/?",Top),
    (r"/admin/left/?",Left),
    (r"/admin/comment/?",CommentList),
    (r"/admin/config/?",Settings),
    (r"/admin/password/?",Password),
]
=======
# -*- coding: UTF-8 -*-
import os,time,math
from common import BaseHandler,render,client_cache,Authentication,render_admin,randomstr
from setting import *
import common
from model import Category,Tag,Post,Comment,BlogConfig,BlogUser
import json
import hashlib
if not debug:
    import sae.mail
    from sae.taskqueue import add_task
    import sae.storage
    



######
def put_obj2storage(file_name = '', data = '', expires='365', type=None, encoding= None, domain_name = STORAGE_DOMAIN_NAME):
    file_name='attachment/'+file_name
    bucket = sae.storage.Bucket(domain_name)
    bucket.put_object(file_name, data, content_type=type, content_encoding=encoding,metadata={"expires":"365d"})
    return bucket.generate_url(file_name)





class Upload(BaseHandler):
    @Authentication()
    def get(self):
        self.write(render_admin.upload(self.datamap))
    def post(self):
        self.set_header('Content-Type','text/html')
        rspd = {'status': 201, 'msg':'ok'}
        callback = self.get_argument('callback','callback');
        filetoupload = self.request.files['filetoupload']
        isimage = 0
        if filetoupload:
            myfile = filetoupload[0]

            
            try:

                file_type = myfile['filename'].split('.')[-1].lower()
                
                isimage = file_type in ['jpg','jpeg','gif','bmp']
                new_file_name = "%s.%s"% (randomstr(10,2), file_type)
                
            except Exception,e:
                print str(e)
                file_type = ''
                new_file_name = randomstr(10,2)
            ##
            mime_type = myfile['content_type']
            encoding = None
            ###
            
            try:
                attachment_url = put_obj2storage(file_name = new_file_name, data = myfile['body'], expires='365', type= mime_type, encoding= encoding)
            except Exception,e:
                print str(e)
                attachment_url = ''
            
            if attachment_url:
                rspd['status'] = 200
                rspd['filename'] = myfile['filename']
                rspd['msg'] = attachment_url
            else:
                rspd['status'] = 500
                rspd['msg'] = 'put_obj2storage erro, try it again.'
        else:
            rspd['msg'] = 'No file uploaded'

        self.write("""
<script type="text/javascript">
    var data = {};
    data.filetype = '%s';
    
    data.url = '%s';
    data.isimage = %d;
    window.parent.uploadCallBack(data);
</script>""" % (file_type, attachment_url,1 if isimage else 0))
        return        

class Login(BaseHandler):
    def get(self):
        self.write(render_admin.login(self.datamap))
    def post(self):
        username = self.get_argument('username','')
        password = self.get_argument('password','')
       
        rememberme = int(self.get_argument('rememberme',1))
        if self.db.get("select * from py_user where username=%s and password=%s limit 1",username,common.md5(password)):
            self.set_secure_cookie(AUTH_COOKIE_NAME,username,httponly=True,expires_days=rememberme)
            self.redirect('/admin/')
        else:
            self.flash(u'用户名与密码不匹配')
            self.redirect('/admin/login/')

class AdminHomePage(BaseHandler):
    @Authentication()
    def get(self):
        self.datamap['url'] = self.get_argument('url','')
        self.write(render_admin.index(self.datamap))
class CommentList(BaseHandler):
    @Authentication()
    def get(self):
        page = int(self.get_argument('page',1))
        if self.get_argument('act','')=='delete':
            Comment.delete_comment_by_id(int(self.get_argument('id',0)))
        pagesize = 20
        rtn = Comment.get_comments(pagesize=pagesize)
        self.datamap['comments'] = rtn[1]
        self.datamap['count'] = rtn[0]
        self.datamap['pagecount'] = int(math.ceil(float(rtn[0])/pagesize))
        self.write(render_admin.comment(self.datamap))


class EditPost(BaseHandler):
    @Authentication()
    def get(self,id):
        post = Post.get_post_by_id(id,ignorestatus=True)
        self.datamap['category'] = Category.get_categorys()
        self.datamap['tags']     = Tag.get_tags()
        
        self.datamap['post'] = post
        

        self.datamap['chose_tag'] = [x.tag for x in post.tag]
        self.datamap['chose_category'] =[x.category for x in post.category] 
        self.write(render_admin.editpost(self.datamap))
    def post(self,id):
        title  =  self.get_argument('title','')
        content = self.get_argument('content','',strip=False)
        status =  self.get_argument('status',0)
        tag = self.get_arguments('tag',[])
        category = self.get_arguments('category',[])
        input_category = self.get_argument('input_category','')
        input_tag = self.get_argument('input_tag','')
        posttype = self.get_argument('posttype',0)
        alias = self.get_argument('alias','')
        tag = list(set(tag+input_tag.split(',')))
        category = list(set(category+input_category.split(',')))
        commentstatus = self.get_argument('commentstatus',0)
        password = self.get_argument('password','')
        
        if title =='' or content=='':
            self.datamap['message'] = u'标题与内容不能为空'
        else:
            rtn = Post.edit_post(id=id,title = title,content = content,status = status,commentstatus = commentstatus,password = password,tag = tag,category = category,posttype=posttype,alias=alias)
            if rtn:
                self.flash(u'修改成功,<a href="/post/%s/" target="_blank">马上查看</a>' % id)
            else:
                self.flash(u'修改失败')
            self.redirect('/admin/post/edit/'+id+'/')

class AdminAddPost(BaseHandler):
    @Authentication()
    def get(self):
        self.datamap['category'] = Category.get_categorys()
        self.datamap['tags']     = Tag.get_tags()
        self.write(render_admin.admin_newpost(self.datamap))
        
    @Authentication()
    def post(self):
        title  =  self.get_argument('title','')
        content = self.get_argument('content','',strip=False)
        status =  self.get_argument('status',0)
        tag = self.get_arguments('tag',[])
        category = self.get_arguments('category',[])
        input_category = self.get_argument('input_category','')
        input_tag = self.get_argument('input_tag','')
        posttype = self.get_argument('posttype',0)
        alias = self.get_argument('alias','')
        tag = list(set(tag+input_tag.split(',')))
        category = list(set(category+input_category.split(',')))
        commentstatus = self.get_argument('commentstatus',0)
        password = self.get_argument('password','')
        
        if title =='' or content=='':
            self.datamap['message'] = u'标题与内容不能为空'
        else:
            postid = Post.new_post(title = title,content = content,status = status,commentstatus = commentstatus,password = password,tag = tag,category = category,alias=alias,posttype=posttype)
            if postid:
                self.redirect('/admin/post/')
            else:
                self.write('faild')

class BlogList(BaseHandler):
    @Authentication()
    def get(self):
        page = int(self.get_argument('page','1'))
        key = self.get_argument('key','')
        act = self.get_argument('act','')
        if act=='delete':
            Post.delete_post_by_id(int(self.get_argument('id',0)))
        pagesize = 20
        count,blogs = Post.get_post(page=page,pagesize=pagesize,showall=True,keyword=key,onlypost=False)

        for x in blogs:
            x.length = len(x.content)
        self.datamap['count'] = count
        self.datamap['posts'] = blogs
        self.datamap['page'] = int(page)
        self.datamap['pagecount'] = int(math.ceil(float(count)/pagesize))
        self.write(render_admin.post(self.datamap))

class Left(BaseHandler):
    def get(self):
        self.write(render_admin.left(self.datamap))


class Top(BaseHandler):
    def get(self):
        self.write(render_admin.top(self.datamap))

class Settings(BaseHandler):
    @Authentication()
    def get(self):
        
        self.write(render_admin.settings(self.datamap))
    def post(self):
        title = self.get_argument('title',u'')
        subtitle = self.get_argument('subtitle','')
        pagesize = int(self.get_argument('pagesize',10))
        enablecomment = self.get_argument('enablecomment',1)
        isclose = self.get_argument('isclose',0)
        BlogConfig.update_configs(title=title,subtitle=subtitle,pagesize=pagesize,enablecomment=enablecomment,isclose=isclose)
        self.flash(u'配置更新成功')
        self.redirect('/admin/config/')

class Password(BaseHandler):
    @Authentication()
    def get(self):
        self.datamap['user'] = BlogUser.get_user_by_username(self.get_current_user)
        self.write(render_admin.password(self.datamap))
    @Authentication()
    def post(self):
        password = self.get_argument('password','')
        newpassword = self.get_argument('newpassword','')
        confirmpassword = self.get_argument('confirmpassword','')
        
        user = BlogUser.get_user_by_username(self.get_current_user)
        email = self.get_argument('email',user.email)
        if password and newpassword and newpassword:
            if newpassword == confirmpassword:
                user = self.db.get("select * from py_user where username=%s limit 1",self.get_current_user)
                if user:
                    if user.password == common.md5(password):
                        rowcount = BlogUser.update_user(self.get_current_user,email,common.md5(newpassword))
                        if rowcount == 1:
                            self.set_secure_cookie(AUTH_COOKIE_NAME,'',expires_days=-10)
                            
                            self.flash(u"密码修改成功，请重新登录。")
                        else:
                            self.flash(u"密码保存失败")
                    else:
                        self.flash(u"原密码验证不正确")
            else:
                self.flash(u"二次输入的密码不一致")
        else:
            BlogUser.update_user(self.get_current_user,email,user.password)
        self.redirect('')

urls = [
    (r"/admin/?", AdminHomePage),
    (r"/admin/post/add/?", AdminAddPost),
    (r"/admin/post/edit/(\d+)/?", EditPost),
    (r"/admin/post/?", BlogList),
    (r"/admin/login/?", Login),
    (r"/admin/upload/?",Upload),
    (r"/admin/top/?",Top),
    (r"/admin/left/?",Left),
    (r"/admin/comment/?",CommentList),
    (r"/admin/config/?",Settings),
    (r"/admin/password/?",Password),
]
>>>>>>> 903cf25d870f2cbcd68c2b4adc2f597bf9c9405a
