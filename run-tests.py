#!/usr/bin/env python

def test(ip):
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
			print e
			pass
		
	return None

if __name__ =='__main__':
	val = test('116.211.23.56')
	print val.encode('utf-8')