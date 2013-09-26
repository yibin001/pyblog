# -*- coding: UTF-8 -*-

import time, datetime
from setting import *
from common import cacheData, deleteCache

try:
    from tornado import database
except:
    import torndb as database

db_master = database.Connection("%s:%s" % (MYSQL_HOST_M, str(MYSQL_PORT)), MYSQL_DB, MYSQL_USER, MYSQL_PASS,
                                max_idle_time=5)
db_slave = database.Connection("%s:%s" % (MYSQL_HOST_S, str(MYSQL_PORT)), MYSQL_DB, MYSQL_USER, MYSQL_PASS,
                               max_idle_time=5)


class Tag(object):
    @cacheData("all_tags")
    def get_tags(self):
        db_slave._ensure_connected()
        return db_slave.query('''SELECT * FROM  `py_tags` ''')

    def add_tag(self, tag, update_postcount=False):
        if not tag:
            return None
        rtn = db_slave.get("select id from py_tags where tag =%s", tag)
        db_master._ensure_connected()
        if not rtn:
            rtn = db_master.execute_lastrowid("insert into py_tags(tag,postcount) values (%s,0)", tag)
            deleteCache("all_tags")
        else:
            rtn = rtn['id']

        if update_postcount:
            db_master.execute("update py_tags set postcount = postcount + 1 where id=%s", rtn)
        return rtn

    def get_tag_by_postid(self, postid):
        db_slave._ensure_connected()
        sql = "select * from py_post_tag where postid=%s"
        query = db_slave.query(sql, postid)

        rtn = []
        if query:
            tags = self.get_tags()

            for q in query:
                tag = [x for x in tags if x.id == q.tagid]
                if tag:
                    rtn.append(tag[0])
        return rtn


    @cacheData('hot_tags_{size}', 300)
    def get_hot_tag(self, size=10):
        db_slave._ensure_connected()
        sql = "select * from py_tags where postcount > 0 order by postcount desc limit {0}".format(size)
        return db_slave.query(sql)


class Category(object):
    @cacheData("all_categorys")
    def get_categorys(self):
        db_slave._ensure_connected()
        return db_slave.query('SELECT * FROM  `py_category` ')

    def add_category(self, categoryname, update_postcount=False):
        if not categoryname:
            return None
        rtn = db_slave.get("select id from `py_category` where category =%s", categoryname)
        db_master._ensure_connected()
        if not rtn:
            rtn = db_master.execute_lastrowid("insert into `py_category`(category,postcount) values (%s,0)",
                                              categoryname)
            deleteCache("all_categorys")
        else:
            rtn = rtn['id']
        if update_postcount:
            db_master.execute("update `py_category` set postcount = postcount + 1 where id=%s", rtn)
        return rtn


    def get_category_by_postid(self, postid):
        db_slave._ensure_connected()
        sql = "select * from py_post_category where postid=%s"
        query = db_slave.query(sql, postid)
        rtn = []
        if query:
            categorys = self.get_categorys()
            for q in query:
                category = [x for x in categorys if x.id == q.categoryid]
                if category:
                    rtn.append(category[0])
        return rtn


Category = Category()
Tag = Tag()


class Post(object):
    def _decrationPost(self, post):
        """
        对于post实体的包装器，封装完整url
        @param post:
        """
        post.url = '/%s/%s/' % ('post' if post.posttype == 0 else 'page', post.id if post.alias == '' else post.alias)

    @cacheData('pages')
    def get_pages(self):
        sql = "select id,title,alias,posttype from py_posts where posttype = 1 and status = 0"
        db_slave._ensure_connected()
        rtn = db_slave.query(sql)
        for x in rtn:
            self._decrationPost(x)
        return rtn


    def get_post(self, page=1, pagesize=10, tag='', category='', showall=False, keyword=None, onlypost=True):
        sql = "select * from py_posts where 1 = 1  "
        if not showall:
            sql += " and status = 0 "
        if onlypost:
            sql += " and posttype = 0 "
        if keyword:
            sql += " and title like '%%{0}%%' ".format(keyword)
        if tag:
            tags = [x.id for x in Tag.get_tags() if x.tag == tag]
            if tags:
                sql += " and id in (select postid from py_post_tag where tagid = {0})".format(tags[0])
        if category:

            categorys = [x.id for x in Category.get_categorys() if x.category == category]
            print categorys
            if categorys:
                sql += " and id in (select postid from py_post_category where categoryid = {0}) ".format(categorys[0])
        countsql = sql.replace('*', ' count(0) as count ')
        sql += " order by id desc limit {0},{1}".format((page - 1) * pagesize, pagesize)
        db_slave._ensure_connected()
        rtn = [0, None]
        rtn[0] = db_slave.get(countsql)['count']
        rtn[1] = db_slave.query(sql)
        for x in rtn[1]:
            self._decrationPost(x)
            more = x.content.find('[more]')
            x.hasmore = False
            if more > -1:
                x.hasmore = True
                x.summary = x.content[:more]
            else:
                x.summary = x.content
        return rtn

    @cacheData("recent_{pagesize}")
    def get_recent_post(self, pagesize=10):
        sql = "select * from py_posts where status = 0 and posttype = 0 order by id desc limit {0}".format(pagesize)
        db_slave._ensure_connected()
        rtn = db_slave.query(sql)
        for x in rtn:
            self._decrationPost(x)
        return rtn

    def edit_post(self, **params):
        db_master._ensure_connected()
        sql = """
        update py_posts set title=%s,content=%s,status=%s,password=%s,commentstatus=%s,lastmodifyed=%s,posttype=%s,alias=%s where id=%s
        """
        rowcount = db_master.execute_rowcount(sql, params['title'], params['content'], params['status'],
                                              params['password'], params['commentstatus'], int(time.time()),
                                              params['posttype'], params['alias'], params['id'])
        if rowcount == 1:
            if params['tag']:
                db_master._ensure_connected()
                db_master.execute('delete from py_post_tag where postid=%s', params['id'])
                for tag in params['tag']:
                    tagid = Tag.add_tag(tag, True)
                    if tagid:
                        db_master._ensure_connected()
                        db_master.execute("INSERT INTO `py_post_tag` (`postid`, `tagid`) VALUES (%s,%s)", params['id'],
                                          tagid)
            if params['category']:
                db_master._ensure_connected()
                db_master.execute('delete from py_post_category where postid=%s', params['id'])
                for category in params['category']:
                    categoryid = Category.add_category(category, True)
                    if categoryid:
                        db_master._ensure_connected()
                        db_master.execute("INSERT INTO `py_post_category` (`postid`, `categoryid`) VALUES (%s,%s)",
                                          params['id'], categoryid)
        if params['posttype'] == 1:
            deleteCache('pages')
        return rowcount == 1

    def new_post(self, **params):
        db_master._ensure_connected()
        sql = """
        INSERT INTO `py_posts` (`title`, `authorid`, `content`, `status`, `password`, `created`, `viewcount`, `commentcount`, `commentstatus`, `lastmodifyed`,posttype,alias) VALUES (%s, 0, %s, %s, %s, %s, %s, %s, %s, %s,%s,%s)"""
        postId = db_master.execute_lastrowid(sql,
                                             params['title'],
                                             params['content'],
                                             params['status'],
                                             params['password'],
                                             int(time.time()),
                                             1, 0, params['commentstatus'], 0,
                                             params['posttype'],
                                             params['alias']
        )
        if postId:
            if params['posttype'] == 1:
                deleteCache('pages')
            for tag in params['tag']:

                tagid = Tag.add_tag(tag, True)
                if tagid:
                    db_master._ensure_connected()
                    db_master.execute("INSERT INTO `py_post_tag` (`postid`, `tagid`) VALUES (%s,%s)", postId, tagid)
            for category in params['category']:
                categoryid = Category.add_category(category, True)
                if categoryid:
                    db_master._ensure_connected()
                    db_master.execute("INSERT INTO `py_post_category` (`postid`, `categoryid`) VALUES (%s,%s)", postId,
                                      categoryid)
            return postId
        return 0


    def delete_post_by_id(self, id):
        sql = "delete from `py_posts` where id=%s"

        db_master._ensure_connected()
        db_master.execute(sql, id)
        tags = db_master.query("select tagid from py_post_tag where postid=%s", id)
        categorys = db_master.query("select categoryid from py_post_category where postid=%s", id)
        db_master.execute("delete from py_comment where postid=%s", id)
        for tag in tags:
            db_master.execute("update py_tags set postcount = postcount - 1 where id=%s and postcount > 0",
                              tag['tagid'])
        for category in categorys:
            db_master.execute("update py_category set postcount = postcount - 1 where id=%s and postcount > 0",
                              category['categoryid'])
        db_master.execute("delete from py_post_tag where postid=%s", id)
        db_master.execute("delete from py_post_category where postid=%s", id)


    def get_post_by_alias(self, alias, ignorestatus=False):
        sql = "select * from py_posts where alias = %s limit 1"
        db_slave._ensure_connected()
        row = db_slave.get(sql, alias)
        if row:
            return self.get_post_by_id(row['id'], ignorestatus)
        return None


    def get_post_by_id(self, postid, ignorestatus=False):
        sql = "select * from py_posts where id=%s "
        if not ignorestatus:
            sql += " and status = 0 "
        db_slave._ensure_connected()
        post = db_slave.get(sql, postid)

        if post:
            post.tag = Tag.get_tag_by_postid(post.id)
            post.category = Category.get_category_by_postid(post.id)
            self._decrationPost(post)
            return post
        else:
            return None

    def search_post_by_title(self, key, page=1, pagesize=10, ignorestatus=False):
        key = key.strip()
        rtn = [0, None]
        if key:
            sql = "SELECT * FROM py_posts  where title like '%%{0}%%' and posttype = 0 ".format(key)
            if not ignorestatus:
                sql += " and status = 0 "
            sqlcount = sql.replace('*', ' count(0) as count ')
            db_slave._ensure_connected()
            sql += " order by id desc limit {0},{1}".format((page - 1) * pagesize, pagesize)
            rtn[0] = db_slave.get(sqlcount)['count']
            rtn[1] = db_slave.query(sql)
            for x in rtn[1]:
                self._decrationPost(x)
        return rtn


Post = Post()


class Comment(object):
    def get_comments_by_postid(self, postid, page=1, pagesize=50, isAdmin=False):
        rtn = [0, None]
        db_slave._ensure_connected()
        sql = "select * from py_comment where postid = %s "
        if not isAdmin:
            sql += " and `status` = 0 "

        sql_count = sql.replace('*', 'count(0) as count')
        sql += " order by id asc limit %s,%s "
        rtn[0] = db_slave.get(sql_count, postid)['count']
        rtn[1] = db_slave.query(sql, postid, (page - 1) * pagesize, pagesize)
        return rtn


    def get_comments(self, page=1, pagesize=50):
        rtn = [0, None]
        db_slave._ensure_connected()
        sql = """SELECT p.title, c . * FROM py_comment c LEFT JOIN py_posts p ON c.postid = p.id  ORDER BY c.id DESC LIMIT %s,%s"""
        sql_count = "SELECT count(0) as count FROM py_comment c LEFT JOIN py_posts p ON c.postid = p.id "
        rtn[0] = db_slave.get(sql_count)['count']

        rtn[1] = db_slave.query(sql, (page - 1) * pagesize, pagesize)
        return rtn

    def post_comment(self, **param):

        if not param.has_key('postid'):
            return False
        post = Post.get_post_by_id(param['postid'])
        if not post:
            return False
        sql = """
INSERT INTO `py_comment` (`postid`, `username`, `email`, `created`, `status`, `content`, `parentid`,`ip`,`isspam`,`location`) VALUES (%s,%s,%s,%s,0,%s,%s,%s,%s,%s)
        """
        db_master._ensure_connected()
        param['id'] = db_master.execute_lastrowid(sql,
                                                  param['postid'],
                                                  param['username'],
                                                  param['email'],
                                                  int(time.time()),
                                                  param['content'],
                                                  param['parentid'],
                                                  param['ip'] if param.has_key('ip') else 'unknow',
                                                  param['isspam'] if param.has_key('isspam') else 0,
                                                  param['location'] if param.has_key('location') else ''
        )
        if param['id']:
            db_master.execute("update py_posts set commentcount = commentcount + 1 where id=%s", param['postid'])
            return True
        return False

    def delete_comment_by_id(self, cid):
        db_master._ensure_connected()
        postid = db_master.get("select postid from py_comment where id=%s", cid)['postid']
        if postid:
            rowaffect = db_master.execute_rowcount("delete from `py_comment` where id=%s", cid)
            if rowaffect == 1:
                db_master.execute("update py_posts set commentcount = commentcount - 1 where id=%s", postid)


Comment = Comment()


class Config(object):
    @cacheData("configs")
    def get_configs(self):
        sql = "select * from py_config"
        rtn = {}
        db_slave._ensure_connected()
        for q in db_slave.query(sql):
            rtn[q.config_key] = q.config_value
        return rtn


    def update_configs(self, **data):
        if not data: return
        sql = "truncate table py_config"
        db_master._ensure_connected()
        db_master.execute(sql)
        for k, v in data.items():
            if str(k).strip() != "":
                sql = "INSERT INTO `py_config` (`config_key`, `config_value`) VALUES (%s, %s)"
                db_master._ensure_connected()
                db_master.execute(sql, k.strip(), v)
        deleteCache("configs")


BlogConfig = Config()


class BlogUser(object):
    def get_users(self):
        sql = "select * from py_user"
        db_slave._ensure_connected()
        return db_slave.query(sql)

    def get_user_by_username(self, username):
        sql = "select * from py_user where 1 = 1 and username= %s limit 1 "

        db_slave._ensure_connected()
        return db_slave.get(sql, username)

    def update_user(self, username, email, password):
        sql = "update py_user set email=%s,password=%s where username=%s limit 1 "
        db_master._ensure_connected()
        return db_master.execute_rowcount(sql, email, password, username)


BlogUser = BlogUser()
