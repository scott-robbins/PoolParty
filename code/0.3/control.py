from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
import socket
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

def main():
	nodes = get_node_names()
	
	
	if '-cmd_all' in sys.argv and len(sys.argv) >=3:
		creds, latency = get_cluster_creds(nodes, False)
		for n in nodes:
			cmd = utils.arr2chstr(sys.argv[2:])
			try:
				result = utils.ssh_exec(cmd, creds[n][1], creds[n][0], creds[n][2], True)
			except Exception:
				pass

	elif '-get_file' in sys.argv and len(sys.argv) >= 4:
		remote_file = sys.argv[2]
		peer = sys.argv[3]
		hostname, ip, pword, pk = setup.load_credentials(peer, False)
		rfile = remote_file.split('/')[-1]
		rpath = remote_file.split(rfile)[0]
		if utils.ssh_get_file(rpath, rfile, ip, hostname, pword):
			print '[*] File Received'

	elif '-put_file' in sys.argv and len(sys.argv) >= 5:
		local_file = sys.argv[2]
		remote_path = sys.argv[3]
		peer = sys.argv[4]
		hostname, ip, pword, pk = setup.load_credentials(peer, False)
		if utils.ssh_put_file(local_file, remote_path, ip, hostname, pword):
			print '[*] File Transfer Complete'

	elif '-update_all_code' in sys.argv:
		cmd = 'cd PoolParty; git pull origin'
		creds, latency = get_cluster_creds(nodes, False)
		for n in nodes:
			try:
				result = utils.ssh_exec(cmd, creds[n][1], creds[n][0], creds[n][2], True)
			except Exception:
				pass

	elif '-node_info' in sys.argv and len(sys.argv) >= 3:
		peer = sys.argv[2]
		hostname, ip, pword, pk = setup.load_credentials(peer, False)
		poolpath = '/PoolParty/code/0.3'
		if hostname == 'root':
			rpath = '/root' + poolpath
		else:
			rpath = '/home/%s%s' % (hostname,poolpath)
		utils.execute_python_script(rpath, 'node.py', ip, hostname, pword, False)

	elif '--run-master' in sys.argv:
		# This the mode for running the local machine as a master node in the pool
		creds, latency = get_cluster_creds(nodes, False)
		peerlist = ''
		for i in nodes:
			peerlist += creds[i][0] + '\n'
		open('peerlist.txt','wb').write(peerlist)
		# [1] - Check that all nodes are connected, and are running this software
		for rmt_peer in nodes:
			ip = creds[rmt_peer][1]
			hname = creds[rmt_peer][0]
			pword = creds[rmt_peer][2]
			# The default installation of PoolParty for each node should be
			# in the home folder of the hostame being connected to
			poolpath = '/PoolParty/code/0.3'
			if hname == 'root':
				rpath = '/root' + poolpath
			else:
				rpath = '/home/%s%s' % (hname,poolpath)
			print '- contacting %s' % rmt_peer
			utils.execute_python_script(rpath, 'node.py %s -show' % rmt_peer, ip, hname, pword, False)
			# [2] - Distribute peerlist, request any data the node has to tell
			utils.ssh_put_file(os.getcwd()+'/PoolData/Shares/peerlist.txt', rpath,ip,hname,pword)

		# [3] - 
		

if __name__ == '__main__':
	main()
