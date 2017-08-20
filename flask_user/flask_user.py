import time
from itsdangerous import Signer
import base64
import json
import md5
from pymongo import MongoClient


class User():
    def __init__(self,secret_key):
        #initialize signer
        self.s = Signer(secret_key)
        

    def deserialize(self,request):
        #it runs in framework BEFORE_REQUEST function
        self.cookies = request.cookies
        #check stat in cookie and verify it
        stat_str = str(self.cookies.get('stat'))
        stat_signature = str(self.cookies.get('stat_signature'))
        stat_token = stat_str+'.'+stat_signature
        

        if stat_str=='None' or self.s.validate(stat_token)==False:
            self._create_new_stat(request)
        #if validation success
        else:
            self.stat = json.loads(stat_str)        

        #increase kolvo_visits
        self._increase_kolvo_visits()

        #add actual IP for checking log_token
        self.stat['ip'] = request.environ['REMOTE_ADDR']
        self.log_token = str(self.cookies.get('log_token'))
        #initialize DB
        self._db_init()


    def serialize(self,response):
        #it runs in framework AFTER_REQUEST function
        stat_str = json.dumps(self.stat)

        sign_str = self.s.sign(stat_str)
        last_elem = len(sign_str.split('.'))
        #because dots in IP
        self.stat_signature = sign_str.split('.')[last_elem-1]

        response.set_cookie('stat',value=stat_str,expires='Fri, 31-Dec-9999 23:59:59 GMT')
        response.set_cookie('stat_signature',value=self.stat_signature,expires='Fri, 31-Dec-9999 23:59:59 GMT')

        if self.log_token!='None':
            response.set_cookie('log_token',value=self.log_token)
	else:
            response.set_cookie('log_token','',expires=0)
 


        #increase visits
        return response

    def _create_new_stat(self,request):
        self.stat = {}
        

        self.stat['ip'] = request.environ['REMOTE_ADDR']
        self.stat['first_reg'] = int(time.time())
        self.stat['kolvo_visits'] = 1
        self.stat['_id'] = 'yap'+str(int(time.time()))
        self.stat['last_visit'] = int(time.time()/86400)


    def _increase_kolvo_visits(self):
        new_day = int(time.time()/86400)
        if self.stat.get('last_visit')==None:
            self.stat['last_visit'] = int(time.time()/86400)

        if int(self.stat.get('last_visit'))<new_day:
            self.stat['kolvo_visits'] = self.stat['kolvo_visits']+1
            self.stat['last_visit'] = new_day



    def check_auth(self,roles):

        if self.log_token=='None':
            return 'Error User:Not Login, Please Log IN'

        if self.s.validate(self.log_token)!=True:
	    self.drop_log_token()
            return 'Error User:Not Valid Login Token. Please, Log IN'

        
        self.session = self._get_json(self.log_token)

        if self.session['ip']!=self.stat['ip']:
		self.drop_log_token()
		return 'Error User:Not valid IP. Please, log IN'
        
        
        if (int(time.time()) - int(self.session['ts']))>int(self.session['live_time']):
       		self.drop_log_token()
		return 'Error User:Session nor fresh, please Log IN'

        #check permission
        for each in self.session['roles']:
            if each in roles:
                return True



        return 'Error User:Not enough permission'


        
    def _gen_token(self,user_id,u_doc):

        self.session = {}

        self.session['_id'] = user_id
        self.session['name'] = u_doc['name']
        self.session['ts'] = int(time.time())
        self.session['roles'] = u_doc['roles']
        self.session['live_time'] = u_doc.get('token_live_time')
        self.session['ip'] = self.stat['ip']


        #create JSON from dict and compress
        j = json.dumps(self.session)
        j64 = base64.b64encode(j)

        #create signature
        j64_sign = self.s.sign(j64)    
    
        return j64_sign
    
    def _get_json(self,token):
        if self.s.validate(token)!=True:
            return 'Error User: not valid Log Token'
        
        jb64 = self.s.unsign(token)
        j = base64.b64decode(jb64)
        j = json.loads(j)
        return j


    def login(self,user_name,user_pass):
        #if user id in db and pass is equal md5 with secret

        #check user name and get user doc

        u_doc,u_id = self._db_check_in(user_name)

        if u_doc==False:
            return 'Error User:No such User'

        #check pass
        if self._md5_trans(user_pass)!=u_doc['pass']:
            return 'Error User:Wrong Pass'


        self.log_token = self._gen_token(u_id, u_doc)
        return True


    def registr(self,u_doc):
        user_id = 'yap'+str(int(time.time()))
        if self._db_check_in(u_doc['name'])!=[False,False]:
            return 'Error User:There is user with the name '+u_doc['name']


        u_doc['pass'] = self._md5_trans(u_doc['pass'])
        self._db_add(user_id,u_doc)

	
        return True



    def drop_log_token(self):
        self.log_token = 'None'
        return True

    def _md5_trans(self,rec):
        m = md5.new()
        m.update(rec)
        return m.hexdigest()

    ##########  DB  #################
    def _db_init(self):
	cl = MongoClient('localhost',27017)
	_db = cl['users']
	self.db = _db['users']


    def _db_check_in(self,u_name):

	u_doc = self.db.find_one({'name':u_name})

	if u_doc==None:
		return [False,False]

	return u_doc,u_doc['_id']


    
    def _db_add(self,u_id,user_d):

	user_d['_id'] = u_id
	self.db.insert_one(user_d)


