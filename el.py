#-*- coding: utf-8 -*-

import requests
import json
import time



CONFIG = {}
#CONFIG['host'] = 'http://localhost:9200'
CONFIG['host'] = 'http://127.0.0.1:9200'
#CONFIG['host'] = 'http://46.101.122.41:9200'



#for each method possible only several results:
#'bug' - means exeption or other problem. You can swith print (bug._print = True) and looks into server runtime log
#'Error:...' - publick error, means erro must be bumbpling up to front
#'OK' - positinve execution
#some other responses which is expectable (like lists, dictionaries etc)

#typically each of methods (high level methods, which is the basic, like create_section(),remove_section()...etc) has as first parameter user_name, that is index name


class bug_class():
	def __init__(self):
		self._print = False
		self.flag = False

	def track(self,ar):
		self.flag = True
		if self._print==True:
			for each in ar:
				print each



bug = bug_class()
bug._print = True

def put(url,data):
	try:
		j_str = data if type(data) is str or type(data) is unicode else json.dumps(data)
		j_str = j_str.encode('utf-8') if type(j_str) is unicode else j_str #for rus lit

		w = requests.put(url,j_str)

		if 'error' in json.loads(w.text):
			bug.track(['Error from elastic when PUT request',w.text,url,j_str])
		
		return w.text		
	except:
		bug.track(['Error: Cannot send PUT request to elastic, problems with connection or check url',url, j_str])

def post(url,data):
	try:
		j_str = data if type(data) is str or type(data) is unicode else json.dumps(data)
		j_str = j_str.encode('utf-8') if type(j_str) is unicode else j_str #for rus lit

		w = requests.post(url,j_str)

		if 'error' in json.loads(w.text):
			bug.track(['Error from elastic when POST request'])

		return w.text		
	except:
		bug.track(['Error: Cannot send POST request to elastic, problems with connection or check url'])
		
	

	
def get(url,data):
	try:
		j_str = data if type(data) is str or type(data) is unicode else json.dumps(data)
		j_str = j_str.encode('utf-8') if type(j_str) is unicode else j_str #for rus lit

		w = requests.get(url,data=j_str)
		if 'error' in json.loads(w.text):
			bug.track(['Error from elastic when GET request',url, j_str,w.text])

		return w.text		
	except:
		bug.track(['Send GET request to elastic, problems with the connection or check url',url, j_str])



def delete(url,data):
	try:
		j_str = data if type(data) is str or type(data) is unicode else json.dumps(data)
		j_str = j_str.encode('utf-8') if type(j_str) is unicode else j_str #for rus lit 

		w = requests.delete(url,data=j_str)
		if 'error' in json.loads(w.text):
			bug.track(['Error from elastic when DELETE request'])

		return w.text		
	except:
		bug.track(['Error: Cannot send DELETE request to elastic, problems with connection or check url'])



#on this stage creating mapping for user index
def create_user_idx(name):
	bug.flag = False
	
	d_fin = {}  #create root
	d_fin['code_notes'] = {'properties':{}}   #create type (like table inside index) with properties field for further inserting fileds
	d_fin['sections'] = {'properties':{}}
	
	#set timestamp filed
	d_fin['code_notes']['_timestamp'] = {"enabled":'true',"store":"yes"}
	d_fin['sections']['_timestamp'] = {"enabled":'true',"store":"yes"}

	def prop():

		d_prop = {}
		d_prop['type'] = 'string'
		d_prop['index'] = 'analyzed'
		d_prop['include_in_all'] = 'false'
		return d_prop


	#in SECTION field
	d_fields = {};
	d_fields['name'] = prop()
	d_fields['name']['index'] = 'not_analyzed'
	
	d_fin['sections']['properties'] = d_fields



	#in CODE_NOTES fileds
	d_fields = {}

	d_fields['section'] = prop()
	d_fields['section'] = prop()
	d_fields['comment'] = prop()
	d_fields['code_notes'] = prop()
	d_fields['created'] = prop()
	d_fields['created']['type'] = 'long'
	d_fields['created']['index'] = 'not_analyzed'
	d_fields['section_exact'] = prop()
	d_fields['section_exact']['index'] = 'not_analyzed'  #it is nessesary to pull code notes for exact section
	
	

	d_fin['code_notes']['properties'] = d_fields



	#create index before putting mapping
	put(CONFIG['host']+'/'+name,'')


	#put mapping for sections
	d = {}
	d['sections'] = d_fin['sections']

	print CONFIG['host']+'/'+name+'/_mapping/sections?refresh=true' 
	print d

	res = put(CONFIG['host']+'/'+name+'/_mapping/sections?refresh=true',d)
	#check error
	if bug.flag==True:
		bug.track(['Cannot create new mapping'])
		return 'bug'

	print 'created'
	#put mapping for code_notes
	d = {}
	d['code_notes'] = d_fin['code_notes']
	res = put(CONFIG['host']+'/'+name+'/_mapping/code_notes?refresh=true',d)

	if bug.flag==True:
		bug.track(['Cannot create new mapping'])
		return 'bug'

	return 'OK'


# on this stage - creating checking the same name existing and if no - creating the name
def create_section(user_name, name):
	bug.flag = False
	#check the same section
	res = get(CONFIG['host']+'/'+user_name+'/sections/_search','{"query":{"match":{"name":"'+name+'"}}}')
	if bug.flag==True:
		bug.track(['Cannot check section name'])
		return 'bug'

	j = json.loads(res)	
	#if section name exists - return error
	if len(j['hits']['hits'])!=0:
		return 'Error: Section exists yet'


	res = post(CONFIG['host']+'/'+user_name+'/sections/?refresh=true','{"name":"'+name+'"}')
	if bug.flag==True:
		bug.track(['Cannot insert new section name'])
		return 'bug'

	return 'OK'


def get_sections(user_name):
	bug.flag = False

	res = get(CONFIG['host']+'/'+user_name+'/sections/_search?size=1000','{"query":{"match_all":{}},"sort":[{"name":"asc"}]}')
	if bug.flag==True:
		bug.track(['Cannot get list with sections'])
		return 'bug'

	j = json.loads(res)
	return j['hits']['hits']


# on this stage - renaming in SECTION and renaming in each document from CODE_NOTES section&section_exact fields
#refreshing - if 'yes' - created timestamp will be renewed 
def rename_section(user_name,_id,new_name,refresh='no'):
	bug.flag = False


	#get old name for further replacing
	res = get(CONFIG['host']+'/'+user_name+'/sections/'+_id,'')
	if bug.flag==True:
		bug.track(['Error:Cannot get old name'])
		return 'bug'

	#because when get by id - total docs contains in root "_source" but hits
	try:
		old_name = json.loads(res)['_source']['name']
	except:
		return 'Error: There is no section by such ID'

	#rename in SECTIONS
	res = put(CONFIG['host']+'/'+user_name+'/sections/'+_id+'?refresh=true','{"name":"'+new_name+'"}')	
	if bug.flag==True:
		bug.track(['Cannot rename section name in SECTION type'])
		return 'bug'

	#rename all docs
	res = get(CONFIG['host']+'/'+user_name+'/code_notes/_search?size=1000000','{"query":{"match":{"section_exact":"'+old_name+'"}},"sort":[{"created":"asc"}]}')
	
	if bug.flag==True:
		bug.track(['Cannot obtain all docs from CODE_NOTES type to change name field'])
	docs = json.loads(res)['hits']['hits']   #get all docs (clear _source) for update
	for each in docs:   #update each doc, it will be deleted and putted again n elastic (to provide reindex). Also version will increment
		_id = each['_id']
		#rename section 
		each = each['_source']
		each['section'] = new_name
		each['section_exact'] = new_name
		if refresh=='yes':
			each['created'] = long(time.time()*1000)   #refresh creation time stamp
	
		new_d = put(CONFIG['host']+'/'+user_name+'/code_notes/'+_id+'?refresh=true',each)
		if bug.flag==True:
			bug.track(['Cannot rename section field in docs from CODE_NOTES type'])
			return 'bug'
 
	return 'OK'
		


def create_note(user_name,data):
	bug.flag = False


	if type(data) is str:
		data = json.loads(data)

	data['section_exact'] = data['section'] #add the same section name to new field for exact searching (pull all docs to section in front)
	data['created'] = long(time.time()*1000)
	
	res = post(CONFIG['host']+'/'+user_name+'/code_notes/?refresh=true',data)
	if bug.flag==True:
		bug.track(['Cannot create code note'])
		return 'bug'

	return 'OK'



#it will update all fileds in data which will be founded in doc
def update_note(user_name,_id, data):
	bug.flag = False


	#first - get current doc
	res = get(CONFIG['host']+'/'+user_name+'/code_notes/'+_id,'')
	if bug.flag==True:
		bug.track(['Cannot get docs when update it'])
		return 'bug'

	doc = json.loads(res)['_source']

	#check data type and insert new values in doc
	data = data if type(data) is dict else json.loads(data)
	for each in data:
		try:
			doc[each] = data[each]
		except:
			pass


	#insert new values into ELastic
	res = put(CONFIG['host']+'/'+user_name+'/code_notes/'+_id+'?refresh=true',doc)
	if bug.flag==True:
		bug.track(['Error:Cannot create code note!'])
		return 'bug'


	return 'OK'
	


def remove_note(user_name,_id):
	bug.flag = False


	res = delete(CONFIG['host']+'/'+user_name+'/code_notes/'+_id+'?refresh=true','')
	if bug.flag==True:
		bug.track(['Cannot delete notes'])
		return 'bug'
	
	return 'OK'


#send note form one section to another. It provided in next way - changing only the name of section field (section_exact& section)
def dispatch_note(user_name,_id,new_section_id):
	bug.flag = False


	#get new sectrion id, it is because of possible problems when transmit string name (rus litters), better tuse ID
	res = get(CONFIG['host']+'/'+user_name+'/sections/'+new_section_id,'')
	if bug.flag==True:
		bug.track(['Cannot get doc from SECTION TYPE when dispatching note'])
		return 'bug'

	try:
		new_section = json.loads(res)['_source']['name']
	except:
		return "Error: There is no SECTION with such id"


	#get doc
	res = get(CONFIG['host']+'/'+user_name+'/code_notes/'+_id,'{"query":{"match_all":{}}}')
	if bug.flag==True:
		bug.track(['Cannot obtain doc from CODE_NOTES type'])


	doc = json.loads(res)['_source']
	doc['section'] = new_section
	doc['section_exact'] = new_section
	doc['created'] = long(time.time()*1000)


	#update doc
	res = put(CONFIG['host']+'/'+user_name+'/code_notes/'+_id+'?refresh=true',doc)
	if bug.flag==True:
		bug.track(['Cannot put new doc to CODE_NOTES'])
		return 'bug'


	return 'OK'




def get_notes(user_name,section_id):
	bug.flag = False


	#get section name
	res = get(CONFIG['host']+'/'+user_name+'/sections/'+section_id,'')
	if bug.flag==True:
		bug.track(['Cannot get SECTION name  by sectionsection_id'])
		return 'bug'

	try:	
		section_name = json.loads(res)['_source']['name']
	except:
		return 'Error: There is no section name by such id'


	#get ntoes by section name
	d = {}
	res = get(CONFIG['host']+'/'+user_name+'/code_notes/_search?size=1000000',{"query":{"match":{"section_exact":section_name}},"sort":[{"created":"asc"}]})

	if bug.flag==True:
		bug.track(['Cannot get document from CODE_NOTES by section name'])
		return 'bug'


	j = json.loads(res)	
	return j['hits']['hits']




def search_notes(user_name,qr):
	bug.flag = False


	res = get(CONFIG['host']+'/'+user_name+'/code_notes/_search?size=1000000',{"query":{"fuzzy_like_this":{"like_text":qr,"fields":["section","code_note","comment"]}}})

	if bug.flag==True:
		bug.track(['Cannot execute search request'])
		return 'bug'


	j = json.loads(res)
	return j['hits']['hits']






def remove_section(user_name,section_id,dispatch_id='no'):
	bug.flag = False

	#get section name for further obtainig docs from code_notes and delete them
	res = get(CONFIG['host']+'/'+user_name+'/sections/'+section_id,'')
	if bug.flag==True:
		bug.track(['Cannot get SECTION name  by section_id'])
		return 'bug'
	
	try:
		section_name = json.loads(res)['_source']['name']
	except:
		return "Error: There is no section by such ID"

	#if dispatch is nessesary (merged in front)
	if dispatch_id!='no':
		#get target section name
		res = get(CONFIG['host']+'/'+user_name+'/sections/'+dispatch_id,'')
		if bug.flag==True:
			bug.track(['Cannot get TARGET SECTION name  by dispatch_id'])
			return 'bug'
		target_name = json.loads(res)['_source']['name']
		rename_section(user_name,section_id,target_name,'yes')
	else:
		#delete the all code_notes
		res = delete(CONFIG['host']+'/'+user_name+'/code_notes/_query?refresh=true','{"query":{"match":{"section_exact":"'+section_name+'"}}}')
		if bug.flag==True:
			bug.track(['Cannot DELETE BULK code notes by section_name'])
			return 'bug'

	if bug.flag==True:
		bug.track(['Cannot go further, bug durind deleting all docs or renaming'])
		return 'bug'

	#remove section from SECTIONS
	res = delete(CONFIG['host']+'/'+user_name+'/sections/'+section_id+'?refresh=true','')
	if bug.flag==True:
		bug.track(['Cannot delete SECTION name  by section_id'])
		return 'bug'

	return 'OK'
	


########CREATE MAPPING##################
#print create_user_idx('andrii')
#bug.flag = False

########CREATE SECTION##################
#print create_section('andrii','Javascript')
#bug.flag = False
#print create_section('andrii','Javascript')
#bug.flag = False
#print create_section('andrii','Python')
#bug.flag = False
#print create_section('andrii','Angular')



########CREATE NOTE_##################
#bug.flag = False
#print create_note('andrii','{"section":"javascript","comment":"test_comment","code_note":"console.log()"}')

#bug.flag = False
#print create_note('andrii','{"section":"Angular","comment":"test_comment","code_note":"console.log()"}')


########RENAME SECTION##################
#bug.flag = False
#print rename_section('andrii','AVHLPdhGDIafQQU3LRZ','AngularJS') #id -section 


########UPDATE NOTE_##################
#bug.flag = False
#print update_note('andrii','AVHLPsnQDIafQQU3LRap',{"code_note":"console.log('test script')","comment":"new_comment"})



########REMOVE NOTE_##################
#bug.flag = False
#print remove_note('andrii','AVHLPnTHDIafQQU3LRaV')




########DISPATCH NOTE_##################
#bug.flag = False
#print dispatch_note('andrii','AVHLPszFDIafQQU3LRaq','AVHLPdgnDIafQQU3LRZZ')



########GET LIST WITH SECTIONS##################
#bug.flag = False
#w = get_sections('andrii')
#for each in w:
#	print each['_source']




########GET LIST WITH NOTES##################
#bug.flag = False
#w = get_notes('andrii','AVHLPdhGDIafQQU3LRZa')
#for each in w:
#	print each['_source']['comment']


########GET LIST WITH SECTIONS##################
#bug.flag = False
#print remove_section('andrii','AVHOI9HYDIafQQU3LczR')















