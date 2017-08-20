import urllib2
from itsdangerous import Signer
import json
import time
import base64


class cook():
	def __init__(self):
		self.s = {}
		self.s['ip'] = '127.0.0.1'
		self.s['first_reg'] = 1442955065
		self.s['kolvo_visits'] = 1
		self.s['user_id'] = 'yap1442955065'
		self.s['last_visit'] = '16702'
		self.minus_days = 0


		self.sig = Signer('andrii')

	def create(self):
		stat = json.dumps(self.s)
		c = self.sig.sign(str(stat))

		last_elem = len(c.split('.'))
		signature = c.split('.')[last_elem-1]
		cookie = 'stat="'+stat+'";stat_signature='+signature
	
		return cookie

	def create_wrong(self):
		stat = json.dumps(self.s)
		c = self.sig.sign(str(stat))

		last_elem = len(c.split('.'))
		signature = c.split('.')[last_elem-1]
		signature = signature[0:len(signature)-5]

		cookie = 'stat="'+stat+'";stat_signature='+signature
	
		return cookie


	def create_with_login(self,roles=None):
		stat = json.dumps(self.s)
		c = self.sig.sign(str(stat))

		last_elem = len(c.split('.'))
		signature = c.split('.')[last_elem-1]

		if roles==None:
			roles = ['admin']

		log_token = self.gen_token('andrii',roles,86400)

		cookie = 'stat="'+stat+'";stat_signature='+signature+';log_token="'+log_token+'"'
		return cookie


	def gen_token(self,user_id,user_roles,token_live_time):
		self.session = {}

		self.session['user_id'] = user_id
		self.session['ts'] = int(time.time())-self.minus_days
		self.session['roles'] = user_roles
		self.session['live_time'] = token_live_time
		self.session['ip'] = self.s['ip']

        #create JSON from dict and compress
		j = json.dumps(self.session)
		j64 = base64.b64encode(j)
		#create signature
		j64_sign = self.sig.sign(j64)

		return j64_sign


	def create_with_wrong_token_login(self):
		stat = json.dumps(self.s)
		c = self.sig.sign(str(stat))

		last_elem = len(c.split('.'))
		signature = c.split('.')[last_elem-1]

		log_token = self.gen_token('andrii',['admin'],86400)

		cookie = 'stat="'+stat+'";stat_signature='+signature+';log_token="'+log_token[0:len(log_token)-3]+'"'

		return cookie

	def create_with_wrong_ip_login(self):
		stat = json.dumps(self.s)
		c = self.sig.sign(str(stat))

		last_elem = len(c.split('.'))
		signature = c.split('.')[last_elem-1]

		log_token = self.gen_token('andrii',['admin'],86400)

		cookie = 'stat="'+stat+'";stat_signature='+signature+';log_token="'+log_token+'"'

		return cookie



print '---------------------------------------------'
print 'STAT TESTING: First_cookie'
print '---------------------------------------------'

req = urllib2.Request('http://localhost:5000')
print "Set-Cookie: "+urllib2.urlopen(req).info()['Set-Cookie']


print '---------------------------------------------'
print 'STAT TESTING: Second Visit'
print '---------------------------------------------'

cook = cook()
cookie = cook.create()
print 'Send: '+cookie
req = urllib2.Request('http://localhost:5000')
req.add_header('Cookie',cookie)


resp = urllib2.urlopen(req)
print 'Set-Cookie:'+resp.info()['Set-Cookie']
print 'Data:'+resp.read()


print '---------------------------------------------'
print 'STAT TESTING: Visit Next Day'
print '---------------------------------------------'

cook.s['last_visit'] = 16700
cookie = cook.create()
print 'Send: '+cookie
req = urllib2.Request('http://localhost:5000')
req.add_header('Cookie',cookie)

resp = urllib2.urlopen(req)
print 'Set-Cookie:'+resp.info()['Set-Cookie']
print 'Data:'+resp.read()



print '---------------------------------------------'
print 'STAT TESTING: Visit wrong signature'
print '---------------------------------------------'

cook.s['last_visit'] = 16700
cookie = cook.create_wrong()
print 'Send: '+cookie
req = urllib2.Request('http://localhost:5000')
req.add_header('Cookie',cookie)

resp = urllib2.urlopen(req)
print 'Set-Cookie:'+resp.info()['Set-Cookie']
print 'Data:'+resp.read()




print '---------------------------------------------'
print 'LogIN TESTING: must be right'
print '---------------------------------------------'


cook.s['last_visit'] = 16702
cookie = cook.create()
print 'Send: '+cookie


req = urllib2.Request('http://localhost:5000/login/andrii/ddd')
req.add_header('Cookie',cookie)

resp = urllib2.urlopen(req)
print 'Set-Cookie:'+resp.info()['Set-Cookie']
print 'Data:'+resp.read()



print '---------------------------------------------'
print 'LogIN TESTING: - wrong pass'
print '---------------------------------------------'


print 'Send: '+cookie


req = urllib2.Request('http://localhost:5000/login/andrii/d')
req.add_header('Cookie',cookie)

resp = urllib2.urlopen(req)
print 'Set-Cookie:'+resp.info()['Set-Cookie']
print 'Data:'+resp.read()



print '---------------------------------------------'
print 'LogIN TESTING: Registr User -> user has registred yet'
print '---------------------------------------------'


print 'Send: '+cookie

req = urllib2.Request('http://localhost:5000/registr/andrii/grf')
req.add_header('Cookie',cookie)

resp = urllib2.urlopen(req)
print 'Set-Cookie:'+resp.info()['Set-Cookie']
print 'Data:'+resp.read()




print '---------------------------------------------'
print 'LogIN TESTING: Registr User -> user has registred'
print '---------------------------------------------'


print 'Send: '+cookie

req = urllib2.Request('http://localhost:5000/registr/andrii_new/grf')
req.add_header('Cookie',cookie)

resp = urllib2.urlopen(req)
print 'Set-Cookie:'+resp.info()['Set-Cookie']
print 'Data:'+resp.read()



print '---------------------------------------------'
print 'LogIN TESTING: Try new user - OK must be'
print '---------------------------------------------'


print 'Send: '+cookie

req = urllib2.Request('http://localhost:5000/login/andrii_new/grf')
req.add_header('Cookie',cookie)

resp = urllib2.urlopen(req)
print 'Set-Cookie:'+resp.info()['Set-Cookie']
print 'Data:'+resp.read()



print '---------------------------------------------'
print 'LOG TOKEN TESTING: Check Auth'
print '---------------------------------------------'



cookie = cook.create_with_login()
print 'Send: '+cookie


req = urllib2.Request('http://localhost:5000')
req.add_header('Cookie',cookie)

resp = urllib2.urlopen(req)
print 'Set-Cookie:'+resp.info()['Set-Cookie']
print 'Data:'+resp.read()


print '---------------------------------------------'
print 'LOG TOKEN TESTING: Check Wrong Token'
print '---------------------------------------------'


cookie = cook.create_with_wrong_token_login()
print 'Send: '+cookie


req = urllib2.Request('http://localhost:5000')
req.add_header('Cookie',cookie)

resp = urllib2.urlopen(req)
print 'Set-Cookie:'+resp.info()['Set-Cookie']
print 'Data:'+resp.read()



print '---------------------------------------------'
print 'LOG TOKEN TESTING: LogIn with wrong IP'
print '---------------------------------------------'


cook.s['ip'] = '124.545.66'
cookie = cook.create_with_wrong_ip_login()
print 'Send: '+cookie


req = urllib2.Request('http://localhost:5000')
req.add_header('Cookie',cookie)

resp = urllib2.urlopen(req)
print 'Set-Cookie:'+resp.info()['Set-Cookie']
print 'Data:'+resp.read()


print '---------------------------------------------'
print 'LOG TOKEN TESTING: LogIn not fresh session'
print '---------------------------------------------'


cook.s['ip'] = '127.0.0.1'
cook.minus_days = 89000  #to test fresh login, minus form ts in log_token
cookie = cook.create_with_login()
print 'Send: '+cookie


req = urllib2.Request('http://localhost:5000')
req.add_header('Cookie',cookie)

resp = urllib2.urlopen(req)
print 'Set-Cookie:'+resp.info()['Set-Cookie']
print 'Data:'+resp.read()



print '---------------------------------------------'
print 'LOG TOKEN TESTING: Check roles'
print '---------------------------------------------'

cook.minus_days = 0;
cookie = cook.create_with_login(['admi'])
print 'Send: '+cookie


req = urllib2.Request('http://localhost:5000')
req.add_header('Cookie',cookie)

resp = urllib2.urlopen(req)
print 'Set-Cookie:'+resp.info()['Set-Cookie']
print 'Data:'+resp.read()

print '---------------------------------------------'
print 'LOG TOKEN TESTING: Check roles, must be OK'
print '---------------------------------------------'

cook.minus_days = 0;
cookie = cook.create_with_login()


req = urllib2.Request('http://localhost:5000')
req.add_header('Cookie',cookie)

resp = urllib2.urlopen(req)
print 'Set-Cookie:'+resp.info()['Set-Cookie']
print 'Data:'+resp.read()

print '---------------------------------------------'
print 'LOG TOKEN TESTING: Drop log-token'
print '---------------------------------------------'


cook.minus_days = 0;

req = urllib2.Request('http://localhost:5000/drop')
req.add_header('Cookie',cookie)
print 'Send: '+cookie



resp = urllib2.urlopen(req)
print 'Set-Cookie:'+resp.info()['Set-Cookie']
print 'Data:'+resp.read()

