import multiprocessing
import network
import random
import utils
import time
import sys 
import os

PYVER = int(sys.version.split(' ')[0].split('.')[0])

def create_env():
	if os.path.isfile(os.getcwd()+'.env'):
		print('[!!] Your .env file is already present')
		return False
	else:
		# Add INTERNAL_IP1
		intip = utils.get_internal_addr()
		env_data = ''
	myname = utils.cmd('hostname',False).pop()
	extip  = utils.get_ext_ip()
	intip  = utils.get_internal_addr()
	env_data += ('HOSTNAME=%s\n' % myname)
	env_data += ('EXTERNAL_IP=%s\n' % extip)
	i = 0
	for addr in intip:
		env_data += ('INTERNAL_IP%d=%s\n' % (i+1,intip[0]))
		i += 1
	if PYVER == 2:
		opt = str(raw_input('Enter Server IP: '))
	elif PYVER == 3:
		opt = str(input('Enter Server IP: '))
	env_data += ('CENTRAL_SERVER=%s\n' % opt)
	open('.env','wb').write(env_data)

def initialize_folders():
	# Need Pool Data
	if not os.path.isdir(os.getcwd()+'/PoolData'):
		os.mkdir(os.getcwd()+'/PoolData')
	if not os.path.isfile(os.getcwd()+'/.env'):
		print('[!!] No Environment setup. Creating Now...')
		create_env()
	if not os.path.isdir(os.getcwd()+'/PoolData/Creds'):
		os.mkdir(os.getcwd()+'/PoolData/Creds')
	if not os.path.isdir(os.getcwd()+'/Shares'):
		os.mkdir(os.getcwd()+'/Shares')

def load_local_vars():
	hostname = utils.getenv('HOSTNAME')
	ext_ip = utils.getenv('EXTERNAL_IP')
	int_ip = utils.getenv('INTERNAL_IP1')
	try:
		server = utils.getenv('CENTRAL_SERVER')
	except:
		env_notice()
		exit()
	return hostname, ext_ip, int_ip, server

def register_commandline(ip, mac):
	msg = 'That Peername is already taken, please choose another. (Enter N to exit)'
	if PYVER == 2:
		pname = raw_input('Enter Peer Name: ') # should these be unique? 
		hname = raw_input('Enter Hostname: ')
	elif PYVER == 3:
		pname = input('Enter Peer Name: ') # should these be unique? 
		hname = input('Enter Hostname: ')
	null, pword = utils.create_password()
	added = False
	while not added:
		name = '%s@%s.creds' % (pname, hname)
		if name not in os.listdir(os.getcwd()+'/PoolData/Creds'):
			client = {'hname': hname,
			  'pname': pname,
			  'pword': pword,
			  'MAC': mac,
			  'IP': ip,
			  'name': name}
			pubkey = utils.create_keys(client)
			added = True
		else:
			if raw_input(msg).upper() == 'N':
				added = True
	return added, client

def add_nodes():
	# Now how to setup nodes as efficiently as possible?
	possible_nodes = network.autodiscover_local()
	for ip_addr, MAC in possible_nodes:
		prompt = ('[?] Would you like to add %s as a Peer? [y/n]: ' % ip_addr)
		if PYVER == 2:
			choice = raw_input(prompt).upper()
		elif PYVER == 3:
			choice = input(prompt).upper()
		if choice == 'Y':
			clientAdded, newPeer = register_commandline(ip_addr, MAC)
			if clientAdded:
				print('[*] Adding %s:%s' % (ip_addr, MAC))
				if newPeer['hname']==utils.ssh_exec('whoami', ip_addr, newPeer['hname'], newPeer['pword'], True).pop().replace('\n',''):
					print('[*] Successfully Added %s to Network' % newPeer['pname'])
					# Register by MAC address though, because IP will change over time
					# But save both because IP is much quicker. Try IP first, if fail
					# can use NMAP and the MAC to "identify" previous peer has new IP
					# and then update the config

def test_connections(debug):
	n_threads = 10;	peers = {}
	pool = multiprocessing.Pool(n_threads)
	# Load Peer Credentials 
	peer_list = network.get_node_names()
	random.shuffle(peer_list)
	for node in peer_list:
		n = node.split('/')[-1].split('.')[0]
		host, host_ip, host_pass, host_mac = utils.load_credentials(n, debug)
		# test_cnx = utils.ssh_exec('whoami', host_ip, host, host_pass, False).pop()
		event = pool.apply_async(func=utils.ssh_exec, args=('whoami', host_ip, host, host_pass, False,))
		try:
			test_cnx = event.get(timeout=10).pop()
		except Exception:
			test_cnx = ''
			pass
		except IndexError:
			test_cnx = ''
			pass
		peer = {'hname': host, 
				'ip': host_ip,
				'pword': host_pass,
				'mac': host_mac,
				'connected': False}
		if test_cnx.replace('\n','') == host:
			print('\033[1m\033[33m[*] Connected to %s\033[0m' % node)
			peer['connected'] = True
		else:
			print('\033[1m\033[31m[!] Unable to connect to %s\033[0m' % node)
			# TODO: Search for that MAC address on the network!
		peers[node] = peer
	return peers

def main():
	if len(sys.argv) < 2 or '-test' not in sys.argv:
		initialize_folders()
		add_nodes()
		test_connections(True)
	elif '-test' in sys.argv:
		test_connections(True)

if __name__ == '__main__':
	main()
