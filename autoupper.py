import requests
import subprocess
import os
import datetime
from threading import Timer




def check():
	try:
		w = requests.get('http://127.0.0.1:9200/andrii/code_notes/_search',data='{"query":{"match_all":{}}}')
		return True
	except:
		return False





def interval():
	if check()==False:
		print 'Restart '+str(datetime.datetime.now())
		p = subprocess.Popen('/home/elastic/elasticsearch-1.7.2/bin/elasticsearch',preexec_fn=os.setuid(1001), stdout=subprocess.PIPE,shell=True)
	Timer(30,interval).start()


interval()

