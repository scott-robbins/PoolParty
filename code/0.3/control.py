import setup
import utils 
import time 
import sys 
import os 

def get_cluster_creds(user_nodes, check_cnx):
	node_creds = {}
	ping = {}
	# Get all the credentials for each node 
	for username in user_nodes:
		hname, ip, pword, pkey = setup.load_credentials(username, False)
		if check_cnx:
			start = time.time()
			result = utils.ssh_exec('whoami', ip, hname, pword, False).replace('\n','')
			stop = time.time()
			if result == hname:
				print '[*] Successful Command Execution on %s [%ss]' % (username, str(stop-start))
				node_creds[username] = [hname, ip, pword]
				ping[username] = float(stop-start)
	return node_creds, ping


nodes = ['Server', 'Jetson', 'Kali', 'Raspberry1', 'Raspberry2']
creds, latency = get_cluster_creds(nodes, True)
