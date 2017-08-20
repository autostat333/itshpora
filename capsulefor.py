import urllib2
import urllib
import json
import os
import re


CONFIG = {

	"files_path":"./static/",      #PATH FOR DOWNLOADED FILES (JS, CSS, OTHER FILES like images as an instance)
	"html_file":"./index.html",               #PATH FOR MAIN HTML FILE (HERE WILL BE SEEKING ALL DECLARATIONS AND HERE WILL BE LINKS INJECTION TO HEAD)
	"html_folders":['./static/templates/']  #PATH FOR OTHER HTML FILES WHERE NESSESARY TO SEEK DECLARATIONS  
	}



class capsulefor():


	def __init__(self):

		self.css_d = {}
		self.js_d = {}	


		self.html_head = []


		self.parse_html()
		self.parse_css()
		self.parse_js()


		#get list with html files in folders from CONFIG['html_folders']
		self.__get_html_files()

		#get list with donwloaded files
		try:
			self.list_files = os.listdir(CONFIG['files_path'])
		except:
			self.list_files = []


	def __get_html_files(self):

		self.html_files = []

		for folder in CONFIG['html_folders']:
			try:
				l = len(folder)
				if folder[l-1]!='/':
					folder = folder+'/'
				list_files = os.listdir(folder)
			except:
				print "!!! ERRROR Cannot find foler <"+folder+">, pls, check name."
				list_files = []
			for file_name in list_files:
				if file_name.endswith('.html')==True:
					self.html_files.append(folder+file_name)
					
		#for safe case - remove html_file
		try:
			self.html_files.remove(CONFIG['html_file'])
		except:
			pass	


	def parse_html(self,html_file=CONFIG['html_file']):

		self.declarations = {}
		try:
			t = open(html_file,'r')
			self.html = t.read()
			t.close()
		except:
			self.html = False
			return False

		#find declarations

		m = re.compile('<[^<>]+capsulefor=[^<>]+></[^<>]{3,10}>',re.DOTALL)
		decl_iter = m.finditer(self.html)

		for each in decl_iter:
			txt = each.group()
			fr_name = self._get_frag_name(txt)
			cl_name = self._get_class_name(txt)
			q = cl_name+':'+fr_name
			self.declarations[q] = txt
		


	def parse_css(self):
		try:
			t = open(CONFIG['files_path']+'cap.css','r')
			self.css = t.read()
			t.close()
		except:
			self.css = None


		if self.css!=None:
			m = re.compile(r'CAPSULEFOR.*<.*>',re.DOTALL).finditer(self.css)
			for each in m:
				txt = each.group()
				txt = txt.split('<')[1].split('>')[0]
				txt = self.rem_quote(txt)
				txt = txt.split(';')[0]

				self.css_d[txt] = self.css_d.get(txt,0)+1



	def parse_js(self):
		try:
			t = open(CONFIG['files_path']+'cap.js','r')
			self.js = t.read()
			t.close()
		except:
			self.js = None


		if self.js!=None:
			m = re.compile(r'CAPSULEFOR[^<>]*<[^<>]+>',re.DOTALL).finditer(self.js)
			for each in m:
				txt = each.group()
				txt = txt.split('<')[1].split('>')[0]
				txt = self.rem_quote(txt)
				txt = txt.split(';')[0]
				self.js_d[txt] = self.js_d.get(txt,0)+1
				
		
	def _get_class_name(self,txt):
		m = re.compile(r'class=[\'\"][^\'\"]+[\'\"]',re.DOTALL)
		cl_w = m.search(txt)
		if cl_w!=None:
			cl_name = cl_w.group()
			cl_name = cl_name.replace('class=','')
			return self.rem_quote(cl_name)

		else:
			return 'default'

	def _get_frag_name(self,txt):
		m = re.compile(r'capsulefor=[\'\"][^\'\"]+[\'\"]',re.DOTALL)
		fr_w = m.search(txt)
		if fr_w!=None:
			fr_name = fr_w.group()
			fr_name = fr_name.replace('capsulefor=','')
			return self.rem_quote(fr_name)
		else:
			print 'Error: No fragment name after capsulefor in :'+txt


	def rem_quote(self,txt):
		st = txt.find('"')
		while st!=-1:
			txt = txt.replace('"','')
			st = txt.find('"')


		st = txt.find("'")
		while st!=-1:
			txt = txt.replace("'","")
			st = txt.find("'")

		
		return txt


	#injection

	def get_fragment_data(self,frag):
		try:
			page = urllib.urlopen('http://188.166.80.84/api/fragment/'+frag)
			self.fragment = json.loads(page.read())
			#replace path for IMG and other ifles
			self.fragment['css'] = self.replace_src(self.fragment['css'])
			self.fragment['js'] = self.replace_src(self.fragment['js'])
			self.fragment['html'] = self.replace_src(self.fragment['html'])
	
		except:
			self.fragment = False
			print 'http://188.166.80.84/api/fragment/'+frag 




	def replace_src(self,txt):
		st = txt.find('./cap/')
		while st!=-1:
			txt = txt.replace('./cap/',CONFIG['files_path'])
			st = txt.find('./cap/')
		return txt


	def add_class(self,cl):
		final_css = ''
		l = len(self.fragment['css'])-1
		flag = 0
		class_start = 0

		char_l = ['\n','\t','\r',' ','\\','*','/','{']

		for each in xrange(l,-1,-1):
			lit = self.fragment['css'][each]
			if lit=='{':
				flag = 1

			if lit=="@":   #drop if @media
				flag=0
				class_start = 0

			if flag==1 and lit not in char_l:
				class_start = 1
			
			if class_start==1:
				if lit=='\n' or lit=='\r' or lit=='\t':
					final_css = '.'+cl+' '+final_css
					flag = 0
					class_start = 0		
	
			final_css = lit+final_css		 
		return final_css



	def inject_css(self, each):
		try:
			t = open(CONFIG['files_path']+'cap.css','a')
		except:
			l = CONFIG['files_path'].split('/')
			total_path = './'
			for folder in l[1:]:
				if len(folder)!=0:
					total_path = total_path+folder+'/'
					try:
						os.mkdir(total_path)  #if dir exist - raise error
					except:
						pass
						

			t = open(CONFIG['files_path']+'cap.css','a')

		#add class
		if each.split(':')[0]!='default':
			c = self.add_class(each.split(':')[0])
		else:
			c = self.fragment['css']

		for_write = '\n\n/* CAPSULEFOR <'+each+';OPEN>  */\n'+c+'\n/* CAPSULEFOR <'+each+';CLOSE>  *\n/'


		t.write(for_write)
		t.close()


	def inject_js(self,each):
		try:
			t = open(CONFIG['files_path']+'cap.js','a')
		except:
			l = CONFIG['files_path'].split('/')
			total_path = './'
			for each in l[1:]:
				if len(each)!=0:
					total_path = total_path+each+'/'
					try:
						os.mkdir(total_path)  #if dir exist - raise error
					except:
						pass

			t = open(CONFIG['files_path']+'cap.js','a')

		for_write = '\n\n// CAPSULEFOR <'+each+';OPEN>\n'+self.fragment['js']+'\n//CAPSULEFOR <'+each+';CLOSE>\n'

		t.write(for_write)
		self.js_d[each] = 1
		t.close()


	def inject_html(self,each, file_name=CONFIG['html_file']):
		t = open(file_name,'r')
		html = t.read()
		t.close()
		try:	
			body = self.fragment['html'].split('<body>')[1].split('</body>')[0]
		except:
			print 'Error: Fragment HTML code contains <body ....>, could not splitting for injenction'
			return False
			

		txt_old = self.declarations[each]
		txt_new = txt_old.replace('><','>'+body+'<')

		st = 0
		kolvo = 0
		while st!=-1:
			kolvo = kolvo+1
			html = html.replace(txt_old,txt_new)
			st = html.find(txt_old)
		
							
		t = open(file_name,'w')
		t.write(html)	
		t.close()
		return kolvo

	def inject_to_head(self, file_name):
		
		t = open(CONFIG['html_file'],'r')
		html = t.read()
		t.close()	
		try:
			head = re.compile('<head>.*</head>',re.DOTALL).search(html).group()
		except:
			print 'Error: HEAD TAG not closed!!!!!'
			return False
		head = head.replace('</head>','')	
	
		if CONFIG['files_path']+file_name in head:
			return False


		if file_name.endswith('.css')==True:
			css_pat = '\n\t<link rel="stylesheet" type="text/css" href="'+CONFIG['files_path']+file_name+'">'
			head = head+css_pat
		
		if file_name.endswith('.js')==True:
			js_pat = '\n\t<script src="'+CONFIG['files_path']+file_name+'"></script>'
			head = head+js_pat

		head = head+'\n</head>'
		html1 = re.sub(re.compile('<head>.*</head>',re.DOTALL),head,html)
		t = open('./'+CONFIG['html_file'],'w')
		t.write(html1)
		t.close()



	def download_files(self,link_file,f_name):
		try:
			urllib.URLopener().retrieve(link_file,CONFIG['files_path']+f_name)
			self.list_files.append(f_name)
		except:
			print '\t\tError to Download file:'+f_name+', by '+link_file



def main():
	
	print '\n--------------------------------------------------------'

	def handle_html_file(html_file_name):
	

		cap.parse_html(html_file_name)

		if len(cap.declarations)==0:
			print 'No any declarations for Fragment in FILE:'+html_file_name
			return False

		print '-----------------------------------------------'
		print 'Script has found next FRAGMENTS declaration in FILE '+html_file_name+'   :'
		for each in cap.declarations:
			print '\t'+each.split(':')[1]+' , CLASS NAME: '+each.split(':')[0]

			cap.get_fragment_data(each.split(':')[1])  #download data

			if cap.fragment!=False:
				print '\t\tData donwloaded.....OK'

			else:
					print '\t\t!!!Data Not Downloaded. Check fragment name or there is troubles with connection'
	

	
			#CSS INJECT
			if cap.fragment!=False and cap.fragment['css']!='None':
				if each not in cap.css_d:
					cap.inject_css(each)
					print '\t\tCSS injected...................................................OK'
				else:
	
					print '\t\tCAP.CSS contains yet  <'+each+'> directive)...not injected.........'
	
			#JS INJECT
			if cap.fragment!=False and cap.fragment['js']!='None':
				if each.split(':')[1] not in cap.js_d:
					cap.inject_js(each.split(':')[1])
					print '\t\tJS injected...................................................OK'
				else:
					print '\t\tCAP.JS contains yet <'+each.split(':')[1]+'> directive)...not injected......'
	
			#HTML INJECT
			if cap.fragment!=False:
				kolvo = cap.inject_html(each, html_file_name)
				print '\t\tHTML injected "'+str(kolvo)+'" times...................OK'
		
	
	
			#Download files
			if cap.fragment!=False:
				for file_ in cap.fragment['files']:
					if file_['name'] not in cap.list_files:
						cap.download_files(file_['link'], file_['name'])
						print '\t\tFile '+file_['name']+' have been downloaded.........OK'
		
			#inject cap.css and cap.js to the head
			if cap.fragment!=False:
				sort_head = sorted(cap.fragment['head'])
				for file_name in sort_head:
					cap.inject_to_head(cap.fragment['head'][file_name])
		
		

	cap = capsulefor()  #initialize object (parcing files and creating dict)


	if cap.html==False:
		print 'Can not find '+CONFIG['html_file']
		return False
	else:
		handle_html_file(CONFIG['html_file'])


	for html_f_name in cap.html_files:
		handle_html_file(html_f_name)

	print '\n--------------------------------------------------------\n'


if __name__=='__main__':
	main()
