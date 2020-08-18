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
				# print '[*] Successful Command Execution on %s [%ss]' % (username, str(stop-start))
				node_creds[username] = [hname, ip, pword]
				p = float(stop-start)
				ping[username] = p

				# color the print out based on reply speed
				if p <= 0.75:
					print '[*] %s is connected %s[%ss Delay]%s' % (username,utils.BOLD+utils.GREEN, p, utils.FEND)
				if 0.75 < p < 1.5:
					print '[*] %s is connected %s[%ss Delay]%s' % (username,utils.BOLD+utils.YELLOW, p, utils.FEND)
				if 1.5 < p:
					print '[*] %s is connected %s[%ss Delay]%s' % (username,utils.BOLD+utils.YELLOW, p, utils.FEND)
	return node_creds, ping

def get_node_names():
	ns = []
	for n in list(set(utils.cmd('ls PoolData/Creds/*.creds',False))):
		ns.append(n.split('@')[0].split('/')[-1])
	return ns 

def main():
	nodes = get_node_names()
	
	
	if '-cmd_all' in sys.argv and len(sys.argv) >=3:
		creds, latency = get_cluster_creds(nodes, True)
		for n in nodes:
			cmd = utils.arr2chstr(sys.argv[2:])
			try:
				result = utils.ssh_exec(cmd, creds[n][1], creds[n][0], creds[n][2], True)
			except Exception:
				pass

	if '-get_file' in sys.argv and len(sys.argv) >= 4:
		remote_file = sys.argv[2]
		peer = sys.argv[3]
		hostname, ip, pword, pk = setup.load_credentials(peer, False)
		rfile = remote_file.split('/')[-1]
		rpath = remote_file.split(rfile)[0]
		if utils.ssh_get_file(rpath, rfile, ip, hostname, pword):
			print '[*] File Received'

	if '-put_file' in sys.argv and len(sys.argv) >= 5:
		local_file = sys.argv[2]
		remote_path = sys.argv[3]
		peer = sys.argv[4]
		hostname, ip, pword, pk = setup.load_credentials(peer, False)
		if utils.ssh_put_file(local_file, remote_path, ip, hostname, pword):
			print '[*] File Transfer Complete'


if __name__ == '__main__':
	main()
