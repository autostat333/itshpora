#-*- coding: utf-8 -*-
from functools import wraps
from flask import Flask, request,Response, redirect
import os
import sys
import json
import el
import time


#determine path of flask_user library and append to sys.path
current_path = os.path.realpath(__file__).split('/')
l = len(current_path)
current_path[l-1] = 'flask_user'
current_path = '/'.join(current_path)
sys.path.append(current_path)


from flask_user import User





app = Flask(__name__)


@app.before_request
def before_request():
	app.user = User('andrii')
	app.user.deserialize(request)


@app.after_request
def after_request(resp):
	resp = app.user.serialize(resp)
	return resp



def for_role(roles=[]):
	def decorator(f):
		@wraps(f)
		def decorated_function(*args, **kwargs):
			permit = app.user.check_auth(roles)
			
			if permit== True or permit=='Error User:Not Login, Please Log IN':
				
				fin  = f(*args, **kwargs)
				return fin
			else:
				print permit
				return permit
		return decorated_function
	return decorator

def for_role_write(roles=[]):
	def decorator(f):
		@wraps(f)
		def decorated_function(*args, **kwargs):
			permit = app.user.check_auth(roles)
			if permit== True:
				fin  = f(*args, **kwargs)
				return fin
			else:
				return permit
		return decorated_function
	return decorator





@app.route('/')
def start():

	current_path = os.path.realpath(__file__)
	print current_path
	current_path = current_path.split('/')
	current_path = '/'.join(current_path[0:len(current_path)-1])
	print current_path	
	t = open(current_path+'/index.html','r')
	r = t.read()
	t.close()

	return r


@app.route('/login', methods=['POST'])
def login():
	u_doc = json.loads(request.data)
	f = app.user.login(u_doc['name'],u_doc['pass'])
	if f!=True:
		return f

	return 'Logged'


@app.route('/registr',methods=['POST'])
def registr():
	u_doc = json.loads(request.data)
	u_doc['roles'] = ['admin']
	u_doc['token_live_time'] = 86400
	
	u_doc_new = u_doc.copy()
	f = app.user.registr(u_doc_new)

	#send error during registred
	if f!=True:
		return f

	if f==True:
		f = app.user.login(u_doc['name'],u_doc['pass'])

	

	#create new mapping
	print 'Before mapping'
	el.create_user_idx(u_doc['name'])
	print 'After mapping'

	return 'Registred'

@app.route('/user')
@for_role(['admin'])
def ggg():
	user_name_for_login = ''
	try:
		user_name_for_login = app.user.session['name']
	except:
		user_name_for_login = 'Error User'
	return user_name_for_login




@app.route('/drop')
def drop_log():
	app.user.drop_log_token()
	return 'OK'







#CORE REST


@app.route('/section/add',methods=['POST'])
@for_role_write(['admin'])
def section_add():
	d = json.loads(request.data)
	u_name = app.user.session['name']
	#execute
	res = el.create_section(u_name,d['name'])	
	if res=='bug':
		return 'Error: Cannot add section'

	if res.find('Error:')==0:
		return res


	return 'OK'

@app.route('/section/rename',methods=['POST'])
@for_role_write(['admin'])
def section_rename():
	d = json.loads(request.data.decode('utf-8'))
	u_name = app.user.session['name']
	
	res = el.rename_section(u_name,d['_id'],d['new_name'])
	if res=='bug':
		return 'Error: Cannot rename SECTION. Problems with server.'

	if res.find('Error:')==0:
		return res


	return 'OK'	



@app.route('/section/merge',methods=['POST'])
@for_role_write(['admin'])
def section_merge():
	d = json.loads(request.data)
	u_name = app.user.session['name']
	
	res = el.remove_section(u_name,d['_id_from'],d['_id_where'])	
	if res=='bug':
		return 'Error: Cannot MERGE SECTION. Problems with server.'

	if res.find('Error:')==0:
		return res


	return 'OK'	



@app.route('/section/remove',methods=['POST'])
@for_role_write(['admin'])
def section_remove():

	d = json.loads(request.data)
	u_name = app.user.session['name']
	
	res = el.remove_section(u_name,d['_id'])	
	if res=='bug':
		return 'Error: Cannot remove SECTION. Problems with server.'

	if res.find('Error:')==0:
		return res


	return 'OK'	




@app.route('/notes/search',methods=['POST'])
@for_role(['admin'])
def search():

	#to subsitute user on my shpora
	try:
		u_name = app.user.session['name']
	except:
		u_name = 'andrii'


	d = json.loads(request.data)

	res = el.search_notes(u_name,d['query'])
	if res=='bug':
		return 'Error: Cannot execute search request. Problems with server.'

	try:
		if res.find('Error:')==0:
			return res
	except:
		pass


	return json.dumps(res)




@app.route('/section/list',methods=['GET'])
@for_role(['admin'])
def section_list():
	#to subsitute user on my shpora
	try:
		u_name = app.user.session['name']
	except:
		u_name = 'andrii'
	
	w = el.get_sections(u_name)
	d = []
	for each in w:
		tmp = {}
		tmp['id'] = each['_id']
		tmp['name'] = each['_source']['name']
		d.append(tmp)

	j = json.dumps(d)
	return j



@app.route('/section/<section_id>/notes',methods=['GET'])
@for_role(['admin'])
def section_notes(section_id):
	#to subsitute user on my shpora
	try:
		u_name = app.user.session['name']
	except:
		u_name = 'andrii'


	w = el.get_notes(u_name,section_id)
	
	if type(w) is str or type(w) is unicode:
		j=w
	else:
		j = json.dumps(w)
	return j



@app.route('/notes/add',methods=['POST'])
@for_role_write(['admin'])
def notes_add():
	d = json.loads(request.data)
	u_name = app.user.session['name']
	#execute
	res = el.create_note(u_name,d)	
	if res=='bug':
		return 'Error: Cannot add CODE NOTE. Problems with server.'

	if res.find('Error:')==0:
		return res


	return 'OK'


@app.route('/notes/update/<_id>',methods=['POST'])
@for_role_write(['admin'])
def notes_update(_id):
	d = request.data
	u_name = app.user.session['name']
	
	res = el.update_note(u_name,_id,d)

	if res=='bug':
		return 'Error: Cannot update note!'
	
	if res.find('Error:')==0:
		return red

	return 'OK'	



@app.route('/notes/dispatch',methods=['POST'])
@for_role_write(['admin'])
def notes_dispatch():
	d = json.loads(request.data)

	u_name = app.user.session['name']
	#execute
	res = el.dispatch_note(app.user.session['name'],d['id_note'],d['id_section']);
	if res=='bug':
		return 'Error: Cannot dispatch note to another section! Maybe problems with server!'

	if res.find('Error:')==0:
		return res

		
	return 'OK'	



@app.route('/notes/remove/<_id>',methods=['GET'])
@for_role_write(['admin'])
def notes_remove(_id):

	u_name = app.user.session['name']	
	res = el.remove_note(u_name,_id)

	if res=='bug':
		return 'Error: Cannot remove note! Maybe problems with server!'

	if res.find('Error:')==0:
		return res



	return 'OK'	


@app.route('/feedback',methods=['POST'])
def feedback():
	d = request.data

	f_name = str(len(os.listdir('./static/feedback/')))+'.txt'
	t = open('./static/feedback/'+f_name,'w')
	t.write(d)
	t.close()
	return 'OK'






if __name__=='__main__':
	app.run(debug=False, host="46.101.122.41",port=81)
