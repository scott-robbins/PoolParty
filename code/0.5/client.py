from dotenv import load_dotenv
from threading import Thread
import multiprocessing
import network
import random
import utils 
import time
import pool
import sys
import os

load_dotenv()

def env_notice():
	print('[!!] Remember to add your choice for a Central Server in this .env file')
	print('\t- enter a line for your server like: \n\t  CENTRAL_SERVER=10.0.0.1')

def setup_env():
	env_data = ''
	myname = utils.cmd('hostname',False).pop()
	extip  = utils.get_ext_ip()
	intip  = utils.get_internal_addr()
	env_data += ('HOSTNAME=%s\n' % myname)
	env_data += ('EXTERNAL_IP=%s\n' % extip)
	if len(intip) == 1:
		env_data += ('INTERNAL_IP1=%s\n' % intip)
	else:
		ip=1
		for addr in intip:
			env_data += ('INTERNAL_IP%d=%s\n' % (ip, addr))
			ip += 1
	env_notice()
	open(os.getcwd()+'/.env','w').write(env_data)

def initialize_folders():
	# Need Pool Data
	if not os.path.isdir(os.getcwd()+'/PoolData'):
		os.mkdir(os.getcwd()+'/PoolData')
	if not os.path.isfile(os.getcwd()+'/.env'):
		print('[!!] No Environment setup. Creating Now...')
		setup_env()
	if not os.path.isdir(os.getcwd()+'/PoolData/Creds'):
		os.mkdir(os.getcwd()+'/PoolData/Creds')

def load_local_vars():
	hostname = os.getenv('HOSTNAME')
	ext_ip = os.getenv('EXTERNAL_IP')
	int_ip = os.getenv('INTERNAL_IP1')
	try:
		server = os.getenv('CENTRAL_SERVER')
	except:
		env_notice()
		exit()
	return hostname, ext_ip, int_ip, server

def ping_server(server):
	ping = utils.cmd('ping -c 1 %s' % server, False)
	if 'bytes' in (ping[1].split(' ')):
		delay = int(ping[1].split(' ')[-2].split('=')[1])
		print('[*] Can reach Server [%dms ping]' % delay)
	else:
		delay = -1
	return delay

def register_commandline(ip, mac):
	msg = 'That Peername is already taken, please choose another. (Enter N to exit)'
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
			if input(msg).upper() == 'N':
				added = True
	return added, client

def add_nodes():
	# Now how to setup nodes as efficiently as possible?
	possible_nodes = network.autodiscover_local()
	for ip_addr, MAC in possible_nodes:
		prompt = ('[?] Would you like to add %s as a Peer? [y/n]: ' % ip_addr)
		if input(prompt).upper() == 'Y':
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
		except multiprocessing.context.TimeoutError:
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
			print('[*] Connected to %s' % node)
			peer['connected'] = True
		else:
			print('[!] Unable to connect to %s' % node)
			# TODO: Search for that MAC address on the network!
		peers[node] = peer
	return peers

def update_node_code(nodelist, verbose):
	for  n in nodelist:
		h = nodelist[n]['hname']
		i = nodelist[n]['ip']
		p = nodelist[n]['pword'] 
		upCmd = 'cd /home/%s/PoolParty; git pull origin HEAD:master' % h
		Thread(target=utils.ssh_exec,args=(upCmd,i,h,p,verbose)).start()


def main():
	debug = True; start = time.time()
	# Setup This machine on network
	initialize_folders()
	hname, eip, iip, cserve = load_local_vars()
	delay = ping_server(cserve)
	if delay == -1:
		print('[!!] Unable to reach Server. (Check that correct IP was put into .env)')
		remote_serve = False
	else:
		remote_serve = True

	if '-setup' in sys.argv:
		add_nodes()
		exit()

	# Check which nodes are connected to network
	nodes = test_connections(debug)
	if debug:
		msg = '='*40+'\n[*] Initialization Finished. [%ss Elapsed]' % (time.time()-start)
		print(msg)

	# Check Whether remote server should be updated
	if remote_serve and not debug and len(os.listdir(os.getcwd()+'/PoolData/Creds')) > 1:
		upload_opt = input('[*] Credentials Present. Upload to Server? [y/n]: ')
	
	# Initialize the Pool of Workers now that things are setup
	cluster = pool.Pool(nodes, debug)
	try:
		cluster.run()
	except KeyboardInterrupt:
		print('[!!] Killing Pool')
		cluster.running = False
		os.system('rm *.txt *.sh')
		exit()

	if '-update' in sys.argv:
		# Update code on all nodes
		print('[*] Updating code running on %d nodes' % len(nodes.keys()))
		update_node_code(nodes, debug)

if __name__ == '__main__':
	main()
