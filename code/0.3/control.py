from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from threading import Thread
import base64
import socket
import setup
import utils 
import time 
import sys 
import os 

FB = '\033[1m'
FI = '\033[3m'
FR = '\033[31m'
FB = '\033[32m'
FG = '\033[34m'
FE = '\033[0m'

def get_cluster_creds(user_nodes, check_cnx):
	node_creds = {}
	ping = {}
	# Get all the credentials for each node 
	for username in user_nodes:
		hname, ip, pword, pkey = setup.load_credentials(username, False)
		node_creds[username] = [hname, ip, pword]
		if check_cnx:
			start = time.time()
			result = utils.ssh_exec('whoami', ip, hname, pword, False).replace('\n','')
			stop = time.time()
			if result == hname:
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

def load_credentials(nickname, debug):
	if not os.path.isdir(os.getcwd()+'/PoolData/Creds'):
		print '[!!] No credentials Found. Plese Register First!'
		exit()
	found = False
	host  = ''
	key_name = nickname+'.pem'
	for name in os.listdir('PoolData/Creds'):
		if len(name.split('@'))==2:
			if nickname == name.split('@')[0]:
				if debug:
					print '[*] Found Credentials for %s' % nickname
				cred_name = name
				host = name.split('@')[1].split('.creds')[0]
				found = True
	if not found:
		print '[!!] Unable to find username %s' % nickname
		exit()
	if not os.path.isfile(os.getcwd()+'/PoolData/Creds/%s' % key_name):
		print '[!!] No credentials founder for username %s' % host
		exit()
	
	private_key = RSA.importKey(open(os.getcwd()+'/PoolData/Creds/%s' % key_name).read())
	raw_creds = PKCS1_OAEP.new(private_key).decrypt(open(os.getcwd()+'/PoolData/Creds/%s' % cred_name,'rb').read())
	hostname = raw_creds.split('@')[0]
	ip_addr = raw_creds.split('@')[1].split(':')[0]
	password = raw_creds.split(':')[1]
	return host, ip_addr, password, private_key

def test_computational_power():
	nodes = get_node_names()
	creds, null = get_cluster_creds(nodes, False)

def send_peer_list(port, receiver, names):
	sent = False
	print ' [*] Sending Peerlist to %s:%d' % (receiver, port)
	while not sent:
		try:
			s = utils.create_tcp_socket(False)
			s.connect((receiver, port))
			s.send(utils.arr2str(names))
			s.close()
			sent = True
		except socket.error:
			sent = False
			pass
	return sent

def parse_request_file(req_filename, peername):
	raw_req = open(req_filename, 'rb').read().split('\n')
	n_jobs = -1; ops = []
	if len(raw_req) > 1:
		for line in raw_req:
			req_type = line.split(' ')[0]
			if req_type == '!':
				# request for more jobs (worker)
				n_jobs = int(line.split(' more jobs')[0].split(' Can take ')[1])
				if n_jobs > 0:
					print '- %s has bandwidth for %d more tasks' % (peername, n_jobs)
			if req_type == '?':
				op = line.split(' ')[1]
				if op == 'NAT':
					print '- %s is requesting NAT data' % (peername)
					ops.append(op)
				if op == 'Files/Data':
					print '- %s is available for data storage' % peername
					ops.append('Data')
				if op == 'CREDS':
					print '- %s is requesting Peer Credentials' % peername
					ops.append('CREDS')
	else:
		n_jobs = int(raw_req.split(' more jobs')[0].split(' Can take ')[1])
		print '- %s is has bandwidth for %d more tasks' % (peername, n_jobs)
	return n_jobs, ops

def dump_nat_info(net_data):
	names = net_data.keys()
	data = ''
	for name in names:
		try:
			dat = net_data[name]
			name = net_data[name]['node']
			addr = net_data[name]['ext_ip']
			data += '%s: %s\n' % (name, addr)
		except KeyError:
			pass
	return data

def nx_dat_init(ns):
	nx_data = {}
	if not os.path.isdir(os.getcwd()+'/PoolData/NX'):
		os.mkdir(os.getcwd()+'/PoolData/NX')
	cs, latency = get_cluster_creds(ns, False)
	peerlist = ''
	for i in ns:
		node_data = {}
		uname = cs[i][0]
		ip = cs[i][1] # This might not be an external ip!!
		node_data['node'] = i 
		node_data['hostname'] = uname 
		node_data['ip'] = ip
		node_data['passwd'] = cs[i][2]
		nx_data[i] = node_data
		#peerlist += i + '\n' # TODO: peerlist probably needs more info
		peerlist += '%s %s %s\n' % (i, uname, ip)
	open(os.getcwd()+'/PoolData/NX/peerlist.txt','wb').write(peerlist)
	return nx_data, cs

def usage():
	print '[!!] Incorrect Usage'
	print '$ python control.py < mode > '
	print 'Valid Modes: '
	print '\t--cmd-all'
	print '\t--get-file'
	print '\t--put-file'
	print '\t--update-all'
	print '\t--node-info'
	print '\t--run-master'

def check_oneself(peer, netdat, cred):
	i = cred[peer][1]
	h = cred[peer][0]
	p = cred[peer][2]
	# The default installation of PoolParty for each node should be
	# in the home folder of the hostame being connected to
	poolp = '/PoolParty/code/0.3'
	if h == 'root':
		rpath = '/root' + poolp
	else:
		rpath = '/home/%s%s' % (h,poolp)
	utils.execute_python_script(rpath, 'node.py %s -dump_info' % peer, i, h, p, False)
	utils.ssh_get_file(rpath+'/PoolData/NX','self.txt',i,h,p)
	if os.path.isfile(os.getcwd()+'/self.txt'):	
		for line in utils.swap('self.txt', True):
			if '  - External IP' in line.split(': '):
				ext_ip = line.split(': ')[1].replace('\n', '')
				netdat[peer]['ext_ip'] = ext_ip
	return netdat, poolp, i, h, p, rpath

def distribute_peerlist(peer, rpth, netdat, i, h, p):
	ploc = '%s/PoolData' % rpth
	netdat[peer]['peer_loc'] = ploc
	utils.ssh_put_file(os.getcwd()+'/PoolData/NX/peerlist.txt', ploc,i,h,p)
	return netdat

def update_requests(peer, rpth, netdat, i, h, p):
	sreq = 'ls -la %s/PoolData/NX/requests.txt' % rpth
	req_size = utils.ssh_exec(sreq, i, h, p, False)
	req_loc = '%s/PoolData/NX' % rpth
	if len(req_size) > 1:
		print '[*] %s has request data available' % peer
	if utils.ssh_get_file_del(req_loc, 'requests.txt', i, h, p):
		print '[*] request data recieved'
		os.system('mv requests.txt PoolData/NX/%s_req.txt' % peer)
		# Parse requests because some might trigger actions 
		n_tasks, operations = parse_request_file(os.getcwd()+'/PoolData/NX/%s_req.txt'%peer, peer)
	else:
		print '[!!] unable to retrieve request data'
		n_tasks = -1
		operations = []
	# Handle operations the node is requesting
	netdat[peer]['pending_operations'] = operations
	netdat[peer]['task_queue'] = n_tasks
	return netdat

def peer_checkin(peer, netdata, cred):
	netdat, rpath, ip, hname,pword, rpath = check_oneself(peer, netdata, cred)
	# [2] - Distribute peerlist
	netdat = distribute_peerlist(peer, rpath, netdat, ip, hname, pword)
	# [3] - See if node has any new data/requests available
	netdat = update_requests(peer, rpath, netdat, ip, hname, pword)
	return netdat

def upload_nat_data(name, netdata):
	nat_dat = dump_nat_info(netdata)
	open('natdat.txt','wb').write(nat_dat)
	# Distribute peer routing info to this peer
	utils.ssh_put_file(os.getcwd()+'/natdat.txt',
					   netdata[name]['peer_loc']+'/NX',
					   netdata[name]['ip'],
					   netdata[name]['hostname'],
					   netdata[name]['passwd'])
	print '[*] NAT Data sent to %s' % name
	os.remove('natdat.txt')

def upload_creds(name, netdata):
	for file in os.listdir(os.getcwd()+'/PoolData/Creds'):
		fname = os.getcwd()+'/PoolData/Creds/' + file
		utils.ssh_put_file(fname, 
						   netdata[name]['peer_loc']+'/Creds',
						   netdata[name]['ip'],
						   netdata[name]['hostname'],
						   netdata[name]['passwd'])


def main():
	nodes = get_node_names()
	
	
	if '--cmd-all' in sys.argv and len(sys.argv) >=3:
		creds, latency = get_cluster_creds(nodes, False)
		for n in nodes:
			cmd = utils.arr2chstr(sys.argv[2:])
			try:
				Thread(target=utils.ssh_exec, args=(cmd, creds[n][1], creds[n][0], creds[n][2], True)).start()
				# result = utils.ssh_exec(cmd, creds[n][1], creds[n][0], creds[n][2], True)
			except Exception:
				pass

	elif '--get-file' in sys.argv and len(sys.argv) >= 4:
		remote_file = sys.argv[2]
		peer = sys.argv[3]
		hostname, ip, pword, pk = setup.load_credentials(peer, False)
		rfile = remote_file.split('/')[-1]
		rpath = remote_file.split(rfile)[0]
		if utils.ssh_get_file(rpath, rfile, ip, hostname, pword):
			print '[*] File Received'

	elif '--put-file' in sys.argv and len(sys.argv) >= 5:
		local_file = sys.argv[2]
		remote_path = sys.argv[3]
		peer = sys.argv[4]
		hostname, ip, pword, pk = setup.load_credentials(peer, False)
		if utils.ssh_put_file(local_file, remote_path, ip, hostname, pword):
			print '[*] File Transfer Complete'

	elif '--update-all' in sys.argv:
		cmd = 'cd PoolParty; git pull origin'
		creds, latency = get_cluster_creds(nodes, False)
		for n in nodes:
			try:
				result = utils.ssh_exec(cmd, creds[n][1], creds[n][0], creds[n][2], True)
			except Exception:
				pass

	elif '--node-info' in sys.argv and len(sys.argv) >= 3:
		peer = sys.argv[2]
		hostname, ip, pword, pk = setup.load_credentials(peer, False)
		poolpath = '/PoolParty/code/0.3'
		if hostname == 'root':
			rpath = '/root' + poolpath
		else:
			rpath = '/home/%s%s' % (hostname,poolpath)
		utils.execute_python_script(rpath, 'node.py', ip, hostname, pword, False)

	elif '--run-master' in sys.argv:	# TODO: break this code into functions!! its getting messy
		# This the mode for running the local machine as a master node in the pool
		network_data, creds = nx_dat_init(nodes)
		
		# [1] - Check that all nodes are connected, and are running this software
		for rmt_peer in nodes:
			# reduced steps 2-3 to this one function to clean this up
			# cant seem to improve speed with multithreading though because I need results of each loop
			# and cant seem to figure out how to save each loop result while also multithreading
			peer_checkin(rmt_peer, network_data, creds)
			
		# [4] - After cycling through all nodes for updates, service any outstanding
		# operations they were seen to be requesting. 
		for nodename in nodes:
			node_stats = network_data[nodename]
			if 'pending_operations' in node_stats.keys():
				if 'NAT' in node_stats['pending_operations']:
					# compile routing info for this peer
					upload_nat_data(nodename, network_data)
				# If flagged, transfer credentials to the node
				if 'CREDS' in node_stats['pending_operations']:
					print '%s is requesting Peer Credentials ' % nodename
					upload_creds(nodename, network_data)
	else:
		usage()


if __name__ == '__main__':
	main()
