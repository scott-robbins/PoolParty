import multiprocessing
import random
import utils
import sys


CHANNELS = ['BTC', 'Security', 'Music']



def check_for_messages(nodes, channels):
	n_threads = 15; 
	pool = multiprocessing.Pool(n_threads)
	# Load Peer Credentials 
	peer_list = utils.get_node_names()
	random.shuffle(peer_list)
	# check whether any nodes have new data available
	for node in peer_list:
		n = node.split('/')[-1].split('.')[0]
		host, host_ip, host_pass, host_mac = utils.load_credentials(n, False)
		# check each channel
		for ch in channels.keys():
			if n in channels[ch]:
				print('[*] Checking if %s has %s data' % (n, ch))




def test_connections(debug):
	n_threads = 15;	peers = {}
	pool = multiprocessing.Pool(n_threads)
	# Load Peer Credentials 
	peer_list = utils.get_node_names()
	random.shuffle(peer_list)
	for node in peer_list:
		n = node.split('/')[-1].split('.')[0]
		host, host_ip, host_pass, host_mac = utils.load_credentials(n, debug)
		peer = {'hname': host, 
				'ip': host_ip,
				'pword': host_pass,
				'mac': host_mac,
				'connected': False}
		event = pool.apply_async(func=utils.ssh_exec, args=('whoami', host_ip, host, host_pass, False,))
		try:
			test_cnx = event.get(timeout=3).pop().replace('\n','') # a bit on shorter side
		except Exception:
			test_cnx = ''
			pass
		except IndexError:
			test_cnx = ''
			pass
		# Verify whether command was executed correctly
		if test_cnx == host:
			print('\033[1m\033[33m[*] Connected to %s\033[0m' % node)
			peer['connected'] = True
		elif debug:
			print('\033[1m\033[31m[!] Unable to connect to %s\033[0m' % node)
		peers[n] = peer
	return peers



def main():
	if '--setup' in sys.argv:
		utils.initialize_folders()
		utils.add_local_peers_pv2()
	else:
		nodes = test_connections(False)

	if '--cmd' in sys.argv and len(sys.argv) > 2:
		hname = utils.sys.argv[2]
		cmd = utils.arr2chr(sys.argv[3:])
		if hname in nodes.keys():
			i = nodes[hname]['ip']
			h = nodes[hname]['hname']
			p = nodes[hname]['pword']
			result = utils.arr2str(utils.ssh_exec(cmd, i, h, p,False))
			print result
		

if __name__ == '__main__':
	main()
