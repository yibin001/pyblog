
#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#-------------------------------------------------------------------------------
# Name:        模板过滤器
# Purpose:
#
# Author:      yibin
#
# Created:     13-06-2010
# Copyright:   (c) yibin 2010
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import hashlib
import re
import datetime,time
import urllib
import sys
import re

more_re = re.compile('\[more\]',re.I)
gist_re = re.compile('\[gist\](.+)\[/gist\]',re.I)
try:
	import misaka as markdown
except:
	import markdown

facereg = "\[em(\d+)\]"

def int2time(value):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(value))

def date_gmt(value):
    return time.strftime('%a, %d %b %Y %H:%M:%S GMT',time.gmtime(value))



def formattime(value,format='%Y-%m-%d %H:%M'):
    return time.strftime(format, time.localtime(value))

def mail2avatar(value):
    return 'http://www.gravatar.com/avatar/%s?s=48&d=&r=G' % ( hashlib.md5(value.lower()).hexdigest())

def html(value):
	value = more_re.sub('',value)
	rtn = value

	try:
		rtn = markdown.html(value)
		
	except:
		rtn = markdown.markdown(value)
	rtn = re.sub(gist_re,'<script src="\\1"></script>',rtn)
	return rtn

def globalavatar(value,size=36):
	return 'http://0.gravatar.com/avatar/%s?s=%s&d=&r=G' % (hashlib.md5(value).hexdigest(),size)