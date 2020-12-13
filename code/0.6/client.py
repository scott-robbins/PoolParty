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
		update = 'cd /home/%s/Documents/PoolParty/; git pull origin master' % hname
		results[p] = utils.ssh_exec(update, ip, hname, pword, True)
	return results


def main():
	if os.path.isfile('.env'):
		h,e,i,s = setup.load_local_vars()

	peers = setup.test_connections(True)
	print('[*] %d Peers Connected' % count_connected(peers))


	if '--cmd-all' in sys.argv:
		replies = cmd_all(peers, utils.arr2chr(sys.argv[2:]))

	if '--update' in sys.argv:
		update_all(peers)

if __name__ == '__main__':
	main()
