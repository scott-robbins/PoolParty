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
	if n in peers.values():
		p = peers[n]
	else:
		found = False
		nc = 'PoolData/Creds/%s.pem' % n
		if os.path.isfile(os.getcwd()+'/'+nc):
			h, i, p, m = utils.load_credentials(nc.split('/')[-1].split('.')[0],False)
			p = {'hname':h,'ip':i,'pword':p,'mac':m,'connected':True}
			found = True
		else:
			for creds in os.listdir(os.getcwd()+'/PoolData/Creds'):
				cf = os.getcwd()+'/PoolData/Creds/%s' % creds
				if os.path.isfile(cf):
					h,i,p,m = utils.load_credentials(cf.split('/')[-1].split('.')[0],False)
					if i == n:
						p = {'hname':h,'ip':i,'pword':p,'mac':m,'connected':True}
						found = True
						break
		if not found:
			print('[!!] cannot find %s' % n)
			return '','','','',''
	
	ip = p['ip']
	mac = p['mac']
	hname = p['hname']
	pword = p['pword']
	connected = p['connected']
	return ip, mac, hname, pword, connected

def exec_rmt(node, peers, payload):
	result = ''
	i, m, h, p, c = get_creds(node, peers)
	print('[*] Executing following on %s\n$ %s' % (node, payload))
	if c:
		try:
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((i, 54123))
			s.send('EXEC :::: %s' % payload)
			result = s.recv(65535)
			s.close()
		except socket.error:
			print('[!!] Connection Error')
			pass
	else:
		print('[!!] %s Does not appear to be online' % i)
	return result

def list_commands(node, peers):
	result = ''
	i, m, h, p, c = get_creds(node, peers)
	if c:
		try:
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((i, 54123))
			s.send('COMMANDS :::: showme!')
			result = s.recv(65535)
		except socket.error:
			print('[!!] Connection Error')
			pass	
	else:
		print('[!!] %s Does not appear to be online' % i)
	return result

def query_file(node, peers, f, operation):
	result = ''
	i, m, h, p, c = get_creds(node, peers)
	if c:
		try:
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((i, 54123))
			s.send('FILE? :::: %s?%s' % (f,operation))
			result = s.recv(65535)
		except socket.error:
			print('[!!] Connection Error')
			pass
	else:
		print('[!!] %s Does not appear to be online' % i)	
	return result

def help():
	print('\t\t\t~ P O O L  P A R T Y ~ ')
	print('\t[*] - Check Peers with \t$ python client.py --check-peers <ip> ')
	print('\t[*] - Check Shares with \t$ python client.py --check-shares <ip>')
	print('\t[*] - Check Commands with \t$ python client.py --show-commands <ip>')
	print('\t[*] - Execute Cmd/Program with  $ python client.py --exec <ip> <payload>')


def main():
	verbose = True
	peers = []; used = False
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
		used = True

	if '--update' in sys.argv:
		update_all(peers)
		used = True
		exit()

	if '--check-peers' in sys.argv and len(sys.argv) > 1:
		rps = dump_peers(sys.argv[2], peers)
		used = True
		if verbose:
			print(rps)

	if '--check-shares' in sys.argv and len(sys.argv) > 2:
		shares = dump_shares(sys.argv[2], peers)
		used = True
		if verbose:
			print(shares)

	if '--exec' in sys.argv and len(sys.argv) > 3:
		reply = exec_rmt(sys.argv[2], peers, utils.arr2chr(sys.argv[3:]))
		used = True
		print(reply)

	if '--show-commands' in sys.argv and len(sys.argv) > 2:
		print(sys.argv[2])
		reply = list_commands(sys.argv[2], peers)
		used = True
		print(reply)

	if '--file-op' in sys.argv and len(sys.argv) > 4:
		result = query_file(sys.argv[1], peers, sys.argv[3], sys.argv[4])
		used = True
		print(result)

	if '--list-local-peers' in sys.argv:
		for p in peers:
			n = p.split('/')[-1].split('.')[0]
			[h,i,p,m] = utils.load_credentials(n,False)
			print('%s \t %s \t %s' % (n, h, m))

	if not used:
		help()

if __name__ == '__main__':
	main()
