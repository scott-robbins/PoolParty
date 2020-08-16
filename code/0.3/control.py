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

def get_node_names():
	ns = []
	for n in list(set(utils.cmd('ls PoolData/Creds/*.creds',False))):
		ns.append(n.split('@')[0].split('/')[-1])
	return ns 

def main():
	nodes = get_node_names()
	creds, latency = get_cluster_creds(nodes, False)
	


if __name__ == '__main__':
	main()
