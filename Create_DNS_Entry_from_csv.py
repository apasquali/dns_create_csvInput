"""
Script takes imput file, runs through it and assignes IPs based off naming scheme.
"""

import socket
import sys
import requests
import os
import time
import datetime
import logging
import logging.handlers
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings()
###########################################################################################
def assign_ip_address (serverDNS, url, network, user, passwd):
	
	data = {"name~":serverDNS}
	r = requests.get(url + 'record:host', auth=(user,passwd), verify = False, params=data)
	if r.text == "[]":
		data = '{"network":"' + network + '"}'
		r = session.get(url + 'ipv4address', auth=(user,passwd), verify=False, data=data)
		
		r_json = r.json()
		count = 11
		for key in r_json:
			if count >= len(r_json):
				break
			
			if r_json[count]['status'] == 'UNUSED':
				single_ip = r_json[count]['ip_address']
				break
				
			count += 1
		
		data = '{"ipv4addrs": [{"ipv4addr": "' + single_ip + '"}],"name": "' + serverDNS + '"}'
		r = session.post(url + 'record:host', verify=False, data=data)
		if r.status_code != 201:
			print ("Issues with creating " + serverDNS)
			d = {'time': datetime.datetime.now().strftime("%m-%d.%H:%M:%S.%f"), 'executed_on':socket.gethostname(), 'ScriptName':os.path.basename(__file__), 'user':user, 'command': data, 'url': url, 'response':r.status_code, 'message': 'ERROR - Issues creating host' + serverDNS}
			my_logger.debug(d)
			return False
		else:
			print ("Success creating " + serverDNS + ":" + single_ip)
			d = {'time': datetime.datetime.now().strftime("%m-%d.%H:%M:%S.%f"), 'executed_on':socket.gethostname(), 'ScriptName':os.path.basename(__file__), 'user':user, 'message': 'Success creating ' + serverDNS + ":" + single_ip}
			my_logger.debug(d)
			return True
	else:
		print ("Failure, request response was : " + r.text)
		print ("DNS for " + serverDNS + " already exists.")
		d = {'time': datetime.datetime.now().strftime("%m-%d.%H:%M:%S.%f"), 'executed_on': socket.gethostname(), 'ScriptName':os.path.basename(__file__), 'user': user, 'command': data, 'url': url, 'response':r.status_code, 'message': 'ERROR - DNS already exits for ' + serverDNS}
		my_logger.debug(d)
		return False
##########################################################################################
my_logger = logging.getLogger('MyLogger')
my_logger.setLevel(logging.DEBUG)
handler = logging.handlers.SysLogHandler(address = ('172.x.x.x',514))
my_logger.addHandler(handler)
print ("Start time:  " + time.strftime("%m.%d.%H.%M.%S"))
d = {'time': datetime.datetime.now().strftime("%m-%d.%H:%M:%S.%f"), 'executed_on': socket.gethostname(), 'ScriptName':os.path.basename(__file__), 'message': 'Message - Starting python DNS script'}
my_logger.debug(d)
filein = sys.argv[1]
inputFile = open(filein, 'r')
lines = inputFile.readline().strip()
	
while (lines != ""):
	stringTest = lines.split(',')[0]
	if stringTest.lower() == "f5":
		VIPfqdn = lines.split(',')[1]
		enviroment = lines.split(',')[2]
		
	lines = inputFile.readline().strip()
session = requests.Session()	
if "devcorp.com" not in VIPfqdn:
	url = 'https://ipamgm.com/wapi/v2.5/'
	DevDevEnvTest = False
elif "devcorp.com" in VIPfqdn:
	url = 'https://dev-ipamgm.devcorp.com/wapi/v2.5/'
	DevDevEnvTest = True
else:
	print ("something went wrong with finding enviroment")
	d = {'time': datetime.datetime.now().strftime("%m-%d.%H:%M:%S.%f"), 'executed_on': socket.gethostname(), 'ScriptName':os.path.basename(__file__), 'message': 'Message - Something went wrong with setting the enviroment in the csv.'}
	my_logger.debug(d)
	sys.exit(126)
		
try:
	user = os.environ['ib_User']
	print ("user is: " + user)
except:
	print ("User enviroment variable not set. Exiting")
	d = {'time': datetime.datetime.now().strftime("%m-%d.%H:%M:%S.%f"), 'executed_on': socket.gethostname(), 'ScriptName':os.path.basename(__file__), 'message': 'ERROR - User enviroment variable not set.'}
	my_logger.debug(d)
	sys.exit(126)
try:
	passwd = os.environ['ib_Password']
	print ("passwd is: " + passwd)
except:
	print ("Password enviroment variable not set. Exiting")
	d = {'time': datetime.datetime.now().strftime("%m-%d.%H:%M:%S.%f"), 'executed_on': socket.gethostname(), 'ScriptName':os.path.basename(__file__), 'message': 'ERROR - Password enviroment variable not set.'}
	my_logger.debug(d)
	sys.exit(126)
	
inputFile.close()
inputFile = open(filein, 'r')
lines = inputFile.readline().strip()
while (lines != ""):
	serverDNS = lines.split(',')[1]
	serverDNS = serverDNS.lower()
	if DevDevEnvTest == True:
		if 'wb' in serverDNS[3:5]:
			serverDNS = serverDNS + ".devcorp.com"
			result = assign_ip_address (serverDNS, url, "172.28.96.0/24", user, passwd)
			if result == False:
				sys.exit(126)
			lines = inputFile.readline().strip()
			continue
		elif 'ap' in serverDNS[3:5]:
			serverDNS = serverDNS + ".devcorp.com"
			result = assign_ip_address (serverDNS, url, "172.28.93.0/24", user, passwd)
			if result == False:
				sys.exit(126)
			lines = inputFile.readline().strip()
			continue
			
	elif enviroment.lower() == 'cert' or enviroment.lower() == 'dev':
		if 'wb' in serverDNS[3:5]:
			serverDNS = serverDNS + ".com"
			result = assign_ip_address (serverDNS, url, "172.x.x.0/24", user, passwd)
			if result == False:
				sys.exit(126)
			lines = inputFile.readline().strip()
			continue
		elif 'ap' in serverDNS[3:5]:
			serverDNS = serverDNS + ".com"
			result = assign_ip_address (serverDNS, url, "172.x.x.0/24", user, passwd)
			if result == False:
				sys.exit(126)
			lines = inputFile.readline().strip()
			continue
			
	elif enviroment.lower() == 'prod':
		if 'wb' in serverDNS[2:5]:
			serverDNS = serverDNS + ".com"
			result = assign_ip_address (serverDNS, url, "172.x.x.0/24", user, passwd)
			if result == False:
				sys.exit(126)
			lines = inputFile.readline().strip()
			continue
		elif 'ap' in serverDNS[3:5] and 'ar' in serverDNS[:2]:
			serverDNS = serverDNS + ".com"
			result = assign_ip_address (serverDNS, url, "172.x.x.0/24", user, passwd)
			if result == False:
				sys.exit(126)
			lines = inputFile.readline().strip()
			continue
		elif 'ap' in serverDNS[3:5] and 'w2' in serverDNS[:2]:
			serverDNS = serverDNS + ".com"
			result = assign_ip_address (serverDNS, url, "172.x.x.0/24", user, passwd)
			if result == False:
				sys.exit(126)
			lines = inputFile.readline().strip()
			continue
	
	if "devcorp.com" in serverDNS:
		result = assign_ip_address (serverDNS, url, "172.x.x.0/24", user, passwd)
		if result == False:
			sys.exit(126)
		lines = inputFile.readline().strip()
		continue
	elif "company.com" in serverDNS and enviroment.lower() == 'cert':
		result = assign_ip_address (serverDNS, url, "172.x.x.0/24", user, passwd)
		if result == False:
			sys.exit(126)
		lines = inputFile.readline().strip()
		continue
	elif "company.com" in serverDNS and enviroment.lower() == 'prod':
		result = assign_ip_address (serverDNS, url, "172.x.x.0/24", user, passwd)
		if result == False:
			sys.exit(126)
		lines = inputFile.readline().strip()
		continue
			
	lines = inputFile.readline().strip()
print ("End time:  " + time.strftime("%m.%d.%H.%M.%S"))
d = {'time': datetime.datetime.now().strftime("%m-%d.%H:%M:%S.%f"), 'executed_on': socket.gethostname(), 'ScriptName':os.path.basename(__file__), 'message': 'Success - End of Script'}
my_logger.debug(d)
