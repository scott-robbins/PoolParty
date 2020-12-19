import multiprocessing
import network
import base64
import socket
import setup 
import utils
import sys 
import os 


def count_connected(pdict):
	c = 0
	for pn in pdict.keys():
		if pdict[pn]['connected']:
			c += 1
	return c

def cmd_all(peers, cmd):
	replies = {}
	for p in peers.keys():
		ip = peers[p]['ip']
		mac = peers[p]['mac']
		hname = peers[p]['hname']
		pword = peers[p]['pword']
		connected = peers[p]['connected']
		replies[p] = utils.ssh_exec(cmd, ip,hname, pword, True)
	return replies

def update_all(peers):
	results = {}
	for p in peers.keys():
		ip = peers[p]['ip']
		mac = peers[p]['mac']
		hname = peers[p]['hname']
		pword = peers[p]['pword']
		connected = peers[p]['connected']
		update = 'cd Documents/PoolParty/code; bash update.sh'
		results[p] = utils.ssh_exec(update, ip, hname, pword, True)
	return results

def dump_peers(node, peers):
	result = ''
	ip,m,hname,pw,connected = get_creds(node, peers)
	if connected:
		try:
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((ip, 54123))
			s.send(('PEERS :::: Dump!'))
			result = s.recv(65535)
			s.close()
		except socket.error:
			print('[!!] Connection Error')
			return ''
	else:
		print('[!!] Peer %s is not online' % node)
		return ''
	return result

def dump_shares(node, peers):
	result = ''
	ip,mac,hname,pword,connected = get_creds(node, peers)
	if connected:
		try:
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((ip, 54123))
			s.send(('SHARES :::: Dump!'))
			result = s.recv(65535)
			s.close()
		except socket.error:
			print('[!!] Connection Error')
			return ''
	else:
		print('[!!] Peer %s is not online' % node)
		return ''
	return result	

def get_creds(n,peers):
	# maybe be able to handle ip or a hostname
	if n in peers.keys():
		p = peers[n]
	else:
		found = False
		for n in peers.keys():
			# print(peers[n])
			if n in peers[n].values():
				found = True
				p = peers[n]
				break
		if os.path.isfile(os.getcwd()+'/'+n):
			h, i, p, m = utils.load_credentials(n.split('/')[-1].split('.')[0],False)
			p = {'hname':h,'ip':i,'pword':p,'mac':m,'connected':True}
			found = True
		if not found:
			print('[!!] cannot find %s' % n)
			return '','','','',''
	
	ip = p['ip']
	mac = p['mac']
	hname = p['hname']
	pword = p['pword']
	connected = p['connected']
	return ip, mac, hname, pword, connected


def main():
	verbose = True
	peers = []
	if os.path.isfile('.env'):
		h,e,i,s = setup.load_local_vars()

		peers = setup.test_connections(True)
		print('[*] %d Peers Connected' % count_connected(peers))


	if '--cmd-all' in sys.argv:
		if len(peers):
			replies = cmd_all(peers, utils.arr2chr(sys.argv[2:]))
			exit()
		else:
			print('[!!] No peers to command (need creds)')

	if '--update' in sys.argv:
		update_all(peers)
		exit()

	if '--check-peers' in sys.argv and len(sys.argv) > 1:
		rps = dump_peers(sys.argv[2], peers)
		if verbose:
			print(rps)
	if '--check-shares' in sys.argv and len(sys.argv) > 2:
		shares = dump_shares(sys.argv[2], peers)
		if verbose:
			print(shares)



if __name__ == '__main__':
	main()
